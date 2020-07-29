from enum import Enum

import requests
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db.models import PointField
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from sentry_sdk import add_breadcrumb


class EventType(Enum):
    SOCI = "Social"
    MEET = "Meeting"
    WORK = "Work"
    MAPE = "Map Event"
    CONF = "Conference"
    MAPA = "Mapathon"


class Event(models.Model):
    name = models.CharField(max_length=200)

    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    whole_day = models.BooleanField(default=False)

    location_name = models.CharField(max_length=50, blank=True, null=True)
    location = PointField(blank=True, null=True)
    location_address = JSONField(blank=True, null=True)

    link = models.URLField(blank=True, null=True)
    kind = models.CharField(max_length=4, choices=[(x.name, x.value) for x in EventType])
    description = models.TextField(blank=True, null=True, help_text='Tell people what the event is about and what they can expect. You may use Markdown in this field.')

    cancelled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.location:
            self.geocode_location()
        super().save(*args, **kwargs)

    def geocode_location(self):
        nr = requests.get('https://nominatim.openstreetmap.org/reverse', params={'format': 'jsonv2', 'lat': self.location.y, 'lon': self.location.x, 'accept-language': 'en'})
        self.location_address = nr.json().get('address', None)
        if self.location_address is None:
            add_breadcrumb(category='nominatim', level='error', data=nr.json())

    @property
    def location_text(self):
        if not self.location_address:
            return None
        addr = self.location_address
        return ", ".join(filter(lambda x: x is not None, [addr.get('village'), addr.get('town'), addr.get('city'), addr.get('state'), addr.get('country')]))

    @property
    def location_detailed_addr(self):
        # TODO: improve
        if not self.location_address:
            return None
        addr = self.location_address
        return ", ".join(filter(lambda x: x is not None, [self.location_name, addr.get('house_number'), addr.get('road'), addr.get('suburb'), addr.get('village'), addr.get('city'), addr.get('state'), addr.get('country')]))

    class Meta:
        indexes = (
            models.Index(fields=('end',)),
        )


class AnswerType(Enum):
    TEXT = 'Text Field'
    CHOI = 'Choice'
    BOOL = 'Boolean'


class ParticipationQuestion(models.Model):
    event = models.ForeignKey('Event', null=True, on_delete=models.SET_NULL, related_name='questions')
    question_text = models.CharField(max_length=200)
    answer_type = models.CharField(max_length=4, choices=[(x.name, x.value) for x in AnswerType])
    mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ('event', 'id')


class ParticipationQuestionChoice(models.Model):
    question = models.ForeignKey(ParticipationQuestion, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    class Meta:
        ordering = ('question', 'id')


class EventParticipation(models.Model):
    event = models.ForeignKey('Event', null=True, on_delete=models.SET_NULL, related_name='participation')
    user = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    added_on = models.DateTimeField(auto_now_add=True, null=True)


class ParticipationAnswer(models.Model):
    question = models.ForeignKey(ParticipationQuestion, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    answer = models.CharField(max_length=200)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('question', 'user'), name='unique_question_answer'),
        )


class EventLog(models.Model):
    event = models.ForeignKey('Event', related_name='log', on_delete=models.CASCADE)
    data = JSONField()
    created_by = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    osm_id = models.IntegerField(null=True)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.username:
            if self.osm_id:
                self.username = 'osm_' + str(self.osm_id)
            else:
                self.username = str(self.id)
        super().save(*args, **kwargs)

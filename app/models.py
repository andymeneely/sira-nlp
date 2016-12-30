from django.contrib.postgres import fields
from django.db import models


class Review(models.Model):
    id = models.BigIntegerField(primary_key=True)

    created = models.DateTimeField()
    is_open = models.BooleanField(default=False)
    was_committed = models.BooleanField(default=False)
    missed_vulnerability = models.BooleanField(default=False)
    num_messages = models.PositiveIntegerField(default=0)

    document = fields.JSONField(default=dict)

    # Navigations Fields
    bugs = models.ManyToManyField('Bug', through='ReviewBug')

    class Meta:
        db_table = 'review'


class Bug(models.Model):
    id = models.BigIntegerField(primary_key=True)

    type = models.CharField(max_length=25, default='')
    status = models.CharField(max_length=25, default='')

    document = fields.JSONField(default=dict)

    # Navigations Fields
    reviews = models.ManyToManyField('Review', through='ReviewBug')

    class Meta:
        db_table = 'bug'


class Vulnerability(models.Model):
    cve = models.CharField(max_length=15, primary_key=True)
    source = models.CharField(max_length=8, default='monorail')

    # Navigation Fields
    bug = models.ForeignKey('Bug')

    class Meta:
        db_table = 'vulnerability'


class ReviewBug(models.Model):
    review = models.ForeignKey('Review')
    bug = models.ForeignKey('Bug')

    class Meta:
        db_table = 'review_bug'

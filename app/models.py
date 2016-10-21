from django.contrib.postgres import fields
from django.db import models


class Review(models.Model):
    id = models.BigIntegerField(primary_key=True)

    created = models.DateTimeField(null=False)
    is_open = models.BooleanField(default=False)
    is_successful = models.BooleanField(default=False)
    has_bug = models.BooleanField(default=False)
    num_messages = models.PositiveIntegerField(null=False, default=0)

    document = fields.JSONField(null=False, default=dict)

    # Navigations Fields
    bugs = models.ManyToManyField('Bug', through='ReviewBug')

    class Meta:
        db_table = 'review'


class Bug(models.Model):
    id = models.BigIntegerField(primary_key=True)

    type = models.CharField(max_length=25, null=False, default='')
    status = models.CharField(max_length=25, null=False, default='')

    document = fields.JSONField(null=False, default=dict)

    # Navigations Fields
    reviews = models.ManyToManyField('Review', through='ReviewBug')

    class Meta:
        db_table = 'bug'


class Vulnerability(models.Model):
    id = models.CharField(max_length=15, primary_key=True)

    # Navigation Fields
    bug = models.ForeignKey('Bug')

    class Meta:
        db_table = 'vulnerability'


class ReviewBug(models.Model):
    review = models.ForeignKey('Review')
    bug = models.ForeignKey('Bug')

    class Meta:
        db_table = 'review_bug'

# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-14 21:06
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_message_sentiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='complexity',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]

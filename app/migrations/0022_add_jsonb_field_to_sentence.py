# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-20 13:38
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_add_text_field_to_sentence'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentence',
            name='clean_parses',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]

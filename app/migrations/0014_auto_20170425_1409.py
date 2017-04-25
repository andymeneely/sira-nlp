# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-25 14:09
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_sentence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sentence',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sentence',
            name='metrics',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={'complexity': {}, 'politeness': {}, 'sentiment': {}}),
        ),
    ]
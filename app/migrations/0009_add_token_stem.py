# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-08 17:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_add_token_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='stem',
            field=models.TextField(db_index=True, default=''),
        ),
    ]

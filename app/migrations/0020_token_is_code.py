# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-18 19:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_index_review_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='is_code',
            field=models.BooleanField(default=False),
        ),
    ]

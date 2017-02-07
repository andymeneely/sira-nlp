# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 17:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20170202_2106'),
    ]

    operations = [
        migrations.RunSQL(
            'CREATE MATERIALIZED VIEW vw_review_token AS '
            'SELECT DISTINCT t.token, m.review_id '
            'FROM token t JOIN message m ON m.id = t.message_id;'
        ),
        migrations.RunSQL(
            'CREATE INDEX vw_review_token_review_id ON vw_review_token '
            'USING btree (review_id);'
        ),
        migrations.RunSQL(
            'CREATE INDEX vw_review_token_text ON vw_review_token '
            'USING btree (token);'
        ),
        migrations.RunSQL(
            'CREATE MATERIALIZED VIEW vw_review_lemma AS '
            'SELECT DISTINCT t.lemma, m.review_id '
            'FROM token t JOIN message m ON m.id = t.message_id;'
        ),
        migrations.RunSQL(
            'CREATE INDEX vw_review_lemma_review_id ON vw_review_lemma '
            'USING btree (review_id);'
        ),
        migrations.RunSQL(
            'CREATE INDEX vw_review_lemma_lemma ON vw_review_lemma '
            'USING btree (lemma);'
        ),
        migrations.CreateModel(
            name='ReviewLemmaView',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                ('lemma', models.TextField(default='')),
                ('review_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'vw_review_lemma',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ReviewTokenView',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                ('token', models.TextField(default='')),
                ('review_id', models.BigIntegerField()),
            ],
            options={
                'db_table': 'vw_review_token',
                'managed': False,
            },
        ),
    ]

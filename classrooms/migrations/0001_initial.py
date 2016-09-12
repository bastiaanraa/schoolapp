# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-12 12:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClassRoom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('klascode', models.CharField(max_length=10, unique=True)),
                ('klasnaam', models.CharField(max_length=20)),
                ('slug', models.SlugField()),
            ],
        ),
    ]

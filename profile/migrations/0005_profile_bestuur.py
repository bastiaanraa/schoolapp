# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-26 10:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bestuur', '0001_initial'),
        ('profile', '0004_profile_werkgroep'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bestuur',
            field=models.ManyToManyField(blank=True, related_name='bestuur', to='bestuur.Bestuur'),
        ),
    ]

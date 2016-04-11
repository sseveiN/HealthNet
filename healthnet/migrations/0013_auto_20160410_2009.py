# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-11 00:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthnet', '0012_auto_20160410_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='marital_status',
            field=models.IntegerField(blank=True, choices=[(0, 'Unspecified'), (1, 'Widowed'), (2, 'LivingCommonLaw'), (3, 'Divorced'), (4, 'Separated'), (5, 'Single'), (6, 'Married')], default=6, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='sex',
            field=models.IntegerField(blank=True, choices=[(0, 'Unspecified'), (1, 'Male'), (2, 'Female')], default=2, null=True),
        ),
    ]

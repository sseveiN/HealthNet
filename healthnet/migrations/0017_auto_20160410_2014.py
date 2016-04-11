# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-11 00:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthnet', '0016_auto_20160410_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='level',
            field=models.IntegerField(choices=[(0, 'Error'), (1, 'Info'), (2, 'Warning')], default=0),
        ),
        migrations.AlterField(
            model_name='patient',
            name='hospital',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='marital_status',
            field=models.IntegerField(blank=True, choices=[(0, 'Divorced'), (1, 'Separated'), (2, 'Widowed'), (3, 'Single'), (4, 'Unspecified'), (5, 'LivingCommonLaw'), (6, 'Married')], default=6, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='sex',
            field=models.IntegerField(blank=True, choices=[(0, 'Male'), (1, 'Unspecified'), (2, 'Female')], default=2, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-11 00:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthnet', '0015_auto_20160410_2012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='hospitals',
            field=models.ManyToManyField(null=True, to='healthnet.Hospital'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='level',
            field=models.IntegerField(choices=[(0, 'Info'), (1, 'Warning'), (2, 'Error')], default=0),
        ),
        migrations.AlterField(
            model_name='nurse',
            name='hospital',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='marital_status',
            field=models.IntegerField(blank=True, choices=[(0, 'Widowed'), (1, 'Separated'), (2, 'Single'), (3, 'LivingCommonLaw'), (4, 'Married'), (5, 'Divorced'), (6, 'Unspecified')], default=6, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='sex',
            field=models.IntegerField(blank=True, choices=[(0, 'Female'), (1, 'Unspecified'), (2, 'Male')], default=2, null=True),
        ),
    ]

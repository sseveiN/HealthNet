# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-10 23:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthnet', '0004_auto_20160410_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='hospitals',
            field=models.ManyToManyField(default=[], to='healthnet.Hospital'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='level',
            field=models.IntegerField(choices=[(0, 'Info'), (1, 'Error'), (2, 'Warning')], default=0),
        ),
        migrations.AlterField(
            model_name='nurse',
            name='hospital',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='hospital',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='marital_status',
            field=models.IntegerField(blank=True, choices=[(0, 'Single'), (1, 'Separated'), (2, 'Married'), (3, 'LivingCommonLaw'), (4, 'Widowed'), (5, 'Divorced'), (6, 'Unspecified')], default=6, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='sex',
            field=models.IntegerField(blank=True, choices=[(0, 'Female'), (1, 'Male'), (2, 'Unspecified')], default=2, null=True),
        ),
    ]

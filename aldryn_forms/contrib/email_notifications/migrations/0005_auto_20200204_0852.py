# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-02-04 08:52


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_notifications', '0004_fieldconditional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailnotification',
            name='from_email',
            field=models.CharField(blank=True, help_text='Must be from a verified domain', max_length=200, verbose_name='from email'),
        ),
        migrations.AlterField(
            model_name='fieldconditional',
            name='action_type',
            field=models.CharField(choices=[('email', 'CC Email to'), ('redirect-email', 'Redirect email to'), ('redirect', 'Redirect to')], max_length=20, verbose_name='action'),
        ),
    ]

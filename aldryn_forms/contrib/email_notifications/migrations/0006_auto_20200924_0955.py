# Generated by Django 2.2.15 on 2020-09-24 09:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('email_notifications', '0005_auto_20200204_0852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailnotification',
            name='form',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_notifications', to='email_notifications.EmailNotificationFormPlugin'),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='to_user',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='to user'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-01-10 15:00


from django.db import migrations


def forward_migration(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    FormPlugin = apps.get_model('aldryn_forms', 'FormPlugin')
    FormPlugin.objects.using(db_alias).filter(action_backend='no_storage').update(action_backend='none')


def backward_migration(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    FormPlugin = apps.get_model('aldryn_forms', 'FormPlugin')
    FormPlugin.objects.using(db_alias).filter(action_backend='none').update(action_backend='no_storage')


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_forms', '0010_auto_20171220_1733'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formplugin',
            old_name='storage_backend',
            new_name='action_backend',
        ),

        migrations.RunPython(forward_migration, backward_migration),

    ]

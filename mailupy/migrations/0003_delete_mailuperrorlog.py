# Generated by Django 2.1.5 on 2019-02-27 11:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailup', '0002_mailuperrorlog'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MailupErrorLog',
        ),
    ]

# Generated by Django 2.1.5 on 2019-02-27 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailupErrorLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('log', models.TextField()),
            ],
        ),
    ]

# Generated by Django 2.2.5 on 2019-10-22 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(db_index=True, max_length=255, unique=True)),
                ('status', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
    ]

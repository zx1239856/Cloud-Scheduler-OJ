# Generated by Django 2.2.5 on 2019-11-04 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemodel',
            name='error',
            field=models.CharField(default='No infomation.', max_length=255),
        ),
    ]
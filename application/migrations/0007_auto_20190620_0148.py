# Generated by Django 2.2 on 2019-06-20 01:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_auto_20190620_0145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='staff_name',
            field=models.CharField(default='', max_length=20),
        ),
    ]

# Generated by Django 2.2 on 2019-06-20 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0005_emailverifyrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='staff_name',
            field=models.CharField(max_length=20, null=True),
        ),
    ]

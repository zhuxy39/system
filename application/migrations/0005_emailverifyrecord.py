# Generated by Django 2.2 on 2019-06-20 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_auto_20190619_1926'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerifyRecord',
            fields=[
                ('code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=30)),
                ('send_type', models.CharField(max_length=50)),
                ('send_time', models.DateField(auto_now=True)),
            ],
            options={
                'db_table': 'EmailVerifyRecord',
            },
        ),
    ]

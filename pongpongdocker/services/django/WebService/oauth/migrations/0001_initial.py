# Generated by Django 5.0.2 on 2024-02-28 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ids', models.CharField(max_length=50)),
                ('login', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=100)),
            ],
        ),
    ]

# Generated by Django 2.2.10 on 2020-02-17 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("addressbase", "0012_uprn_to_council"),
    ]

    operations = [
        migrations.DeleteModel(name="Onsud",),
    ]
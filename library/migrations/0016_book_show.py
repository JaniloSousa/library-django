# Generated by Django 4.2.1 on 2023-06-01 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0015_delete_profilepic"),
    ]

    operations = [
        migrations.AddField(
            model_name="book", name="show", field=models.BooleanField(default=True),
        ),
    ]

# Generated by Django 2.2.2 on 2019-06-14 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20190614_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='birthday',
            field=models.IntegerField(default=32, null=True),
        ),
    ]

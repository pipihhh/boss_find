# Generated by Django 2.2.2 on 2019-06-14 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190614_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='desc',
            field=models.CharField(default='暂无简介', max_length=1024, null=True),
        ),
    ]

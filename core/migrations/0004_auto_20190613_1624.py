# Generated by Django 2.2.2 on 2019-06-13 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20190613_0339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='user',
            field=models.OneToOneField(limit_choices_to={'userrole': 2}, on_delete=django.db.models.deletion.CASCADE, to='core.User'),
        ),
        migrations.AlterField(
            model_name='user',
            name='account',
            field=models.CharField(max_length=32, unique=True, verbose_name='账号'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=32, verbose_name='密码'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=32, verbose_name='真实姓名'),
        ),
        migrations.AlterField(
            model_name='user',
            name='userrole',
            field=models.SmallIntegerField(choices=[(1, '管理员'), (2, '应聘者'), (3, '公司')], default=2, verbose_name='角色'),
        ),
    ]

# Generated by Django 2.1.2 on 2018-10-18 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('validation', '0005_auto_20181016_0414'),
        ('notifier', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='githubissue',
            name='validation_site',
        ),
        migrations.AddField(
            model_name='githubissue',
            name='validation_group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='validation.ValidationGroup', verbose_name='Validation group'),
            preserve_default=False,
        ),
    ]

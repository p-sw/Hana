# Generated by Django 4.1.3 on 2022-11-14 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]

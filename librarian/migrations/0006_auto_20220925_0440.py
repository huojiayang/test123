# Generated by Django 3.2 on 2022-09-25 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarian', '0005_books_achievement_books_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarian',
            name='achievement',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='成绩'),
        ),
        migrations.AddField(
            model_name='librarian',
            name='status',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='状态'),
        ),
    ]

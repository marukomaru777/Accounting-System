# Generated by Django 5.0.4 on 2024-05-14 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_rename_u_account_category_u_username_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='u_username',
            new_name='username',
        ),
        migrations.RenameField(
            model_name='expenses',
            old_name='u_username',
            new_name='username',
        ),
    ]

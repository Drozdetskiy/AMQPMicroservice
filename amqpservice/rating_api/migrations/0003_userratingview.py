# Generated by Django 2.2.1 on 2019-08-07 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating_api', '0002_refreshlog'),
    ]

    operations = [
        migrations.RunSQL(
            'CREATE MATERIALIZED VIEW rating_api_userratingview AS SELECT id, '
            'ROW_NUMBER() OVER(ORDER BY rating DESC, datetime ASC) AS Row, '
            'user_id, rating, datetime FROM rating_api_userrating;',
            'DROP MATERIALIZED VIEW rating_api_userratingview;'
        ),
    ]


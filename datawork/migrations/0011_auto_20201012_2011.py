# Generated by Django 3.1.1 on 2020-10-12 14:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datawork', '0010_remove_paymentgenerate_pg_room_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentgenerate',
            name='pg_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 12, 20, 11, 58, 959819)),
        ),
        migrations.AlterField(
            model_name='paymentpaid',
            name='pp_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 12, 20, 11, 58, 960816)),
        ),
        migrations.AlterField(
            model_name='room',
            name='r_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 12, 20, 11, 58, 953835)),
        ),
        migrations.AlterField(
            model_name='roomquery',
            name='m_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 12, 20, 11, 58, 958827)),
        ),
    ]

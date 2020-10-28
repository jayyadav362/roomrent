# Generated by Django 3.1.1 on 2020-10-22 15:47

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('datawork', '0022_auto_20201020_0220'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentgenerate',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_owner', to='auth.user'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='paymentgenerate',
            name='pg_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 22, 21, 17, 17, 142697)),
        ),
        migrations.AlterField(
            model_name='paymentgenerate',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_renter', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='paymentpaid',
            name='pp_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 22, 21, 17, 17, 143695)),
        ),
        migrations.AlterField(
            model_name='room',
            name='r_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 22, 21, 17, 17, 138708)),
        ),
        migrations.AlterField(
            model_name='roomallot',
            name='ra_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 22, 21, 17, 17, 141700)),
        ),
        migrations.AlterField(
            model_name='roomquery',
            name='m_doc',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2020, 10, 22, 21, 17, 17, 141700)),
        ),
    ]
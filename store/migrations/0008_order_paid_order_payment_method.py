# Generated by Django 4.0 on 2022-01-13 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_order_razorpay_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Razorpay', 'Razorpay'), ('COD', 'COD')], max_length=20, null=True),
        ),
    ]

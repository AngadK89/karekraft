# Generated by Django 4.0 on 2022-01-06 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_order_complete"),
    ]

    operations = [
        migrations.RenameField(
            model_name="shippingaddress",
            old_name="ate_added",
            new_name="date_added",
        ),
    ]

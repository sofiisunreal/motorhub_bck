from django.db import migrations


def create_legacy_payments(apps, schema_editor):

    Sale = apps.get_model("sales", "Sale")
    Payment = apps.get_model("sales", "Payment")

    for sale in Sale.objects.all():

        # Don't create duplicate payments
        if Payment.objects.filter(sale=sale).exists():
            continue

        Payment.objects.create(
            sale=sale,
            amount=sale.selling_price,
            payment_method="cash",
            reference="Legacy sale",
            received_by=sale.sold_by
        )


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0005_remove_sale_payment_status_and_more"),
    ]

    operations = [
        migrations.RunPython(create_legacy_payments),
    ]

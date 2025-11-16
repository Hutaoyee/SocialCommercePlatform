# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0006_orderitem_is_reviewed_orderitemreview_refundrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_company',
            field=models.CharField(blank=True, max_length=100, verbose_name='物流公司'),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=100, verbose_name='物流单号'),
        ),
    ]

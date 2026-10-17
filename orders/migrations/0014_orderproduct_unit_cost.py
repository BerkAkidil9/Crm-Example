from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0013_orderproduct_unit_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct', name='unit_cost',
            # Older versions never recorded costs. Null means unknown, not zero
            # or the current catalog cost. New lines get a snapshot on save.
            field=models.FloatField(editable=False, null=True),
        ),
    ]

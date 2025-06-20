# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0010_gameorganizationrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="withdrawalrequest",
            name="reference_paiement",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="Référence de paiement"
            ),
        ),
    ]
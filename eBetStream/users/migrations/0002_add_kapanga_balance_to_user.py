# Generated manually

from django.db import migrations, models
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='kapanga_balance',
            field=models.DecimalField(
                decimal_places=2,
                default=0.00,
                max_digits=10,
                validators=[MinValueValidator(0)],
                verbose_name='Solde Kapanga'
            ),
        ),
    ]
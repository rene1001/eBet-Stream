# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_kapanga_balance_to_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='payment_methods/', verbose_name='Logo')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('min_amount', models.DecimalField(decimal_places=2, default=5.0, max_digits=10, verbose_name='Montant minimum')),
                ('max_amount', models.DecimalField(decimal_places=2, default=1000.0, max_digits=10, verbose_name='Montant maximum')),
                ('fee_percentage', models.DecimalField(decimal_places=2, default=0.0, max_digits=5, verbose_name='Frais (%)')),
                ('processing_time', models.CharField(blank=True, max_length=100, verbose_name='Temps de traitement')),
            ],
            options={
                'verbose_name': 'Méthode de paiement',
                'verbose_name_plural': 'Méthodes de paiement',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_method',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='transactions',
                to='users.paymentmethod',
            ),
        ),
    ]
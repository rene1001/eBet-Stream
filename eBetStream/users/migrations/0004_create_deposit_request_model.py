# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_add_payment_method_id_to_transaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepositRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Montant')),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='ID de transaction')),
                ('proof_of_payment', models.ImageField(blank=True, null=True, upload_to='payment_proofs/', verbose_name='Preuve de paiement')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour')),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('approved', 'Approuvé'), ('rejected', 'Rejeté')], default='pending', max_length=10, verbose_name='Statut')),
                ('admin_notes', models.TextField(blank=True, verbose_name='Notes administrateur')),
                ('payment_method', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposit_requests', to='users.paymentmethod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deposit_requests', to='users.user')),
            ],
            options={
                'verbose_name': 'Demande de dépôt',
                'verbose_name_plural': 'Demandes de dépôt',
                'ordering': ['-created_at'],
            },
        ),
    ]
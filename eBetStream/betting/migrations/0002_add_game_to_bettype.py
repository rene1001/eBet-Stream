# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('betting', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bettype',
            name='match',
        ),
        migrations.AddField(
            model_name='bettype',
            name='game',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bet_types', to='core.game', verbose_name='Jeu'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bettype',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='bettype',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Actif'),
        ),
        migrations.AlterField(
            model_name='bettype',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='bettype',
            name='odds',
            field=models.DecimalField(decimal_places=2, default=2.0, max_digits=5, verbose_name='Cote'),
        ),
    ]
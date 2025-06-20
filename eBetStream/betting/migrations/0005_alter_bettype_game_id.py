# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0004_livebet_alter_bet_match_alter_bet_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bettype',
            name='game_id',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bet_types',
                to='core.game',
                verbose_name='Jeu'
            ),
        ),
    ]
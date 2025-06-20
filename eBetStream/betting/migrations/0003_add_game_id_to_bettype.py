# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('betting', '0002_add_game_to_bettype'),
    ]

    operations = [
        migrations.AddField(
            model_name='bettype',
            name='game_id',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bet_types_by_id',
                to='core.game',
                verbose_name='Jeu ID'
            ),
            preserve_default=False,
        ),
    ]
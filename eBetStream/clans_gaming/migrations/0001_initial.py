# Generated by Django 5.2 on 2025-06-16 12:32

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("gameurs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Clan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100, unique=True)),
                (
                    "logo",
                    models.ImageField(blank=True, null=True, upload_to="clans/logos/"),
                ),
                ("jeu", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("nombre_victoires", models.IntegerField(default=0)),
                ("nombre_defaites", models.IntegerField(default=0)),
                ("ratio", models.FloatField(default=0.0)),
            ],
            options={
                "ordering": ["-ratio"],
            },
        ),
        migrations.CreateModel(
            name="MatchClan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_match", models.DateTimeField(default=django.utils.timezone.now)),
                ("score_clan1", models.IntegerField(default=0)),
                ("score_clan2", models.IntegerField(default=0)),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("en_attente", "En attente"),
                            ("en_cours", "En cours"),
                            ("termine", "Terminé"),
                            ("annule", "Annulé"),
                        ],
                        default="en_attente",
                        max_length=20,
                    ),
                ),
                (
                    "clan1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="matches_clan1",
                        to="clans_gaming.clan",
                    ),
                ),
                (
                    "clan2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="matches_clan2",
                        to="clans_gaming.clan",
                    ),
                ),
                (
                    "vainqueur",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="matches_gagnes",
                        to="clans_gaming.clan",
                    ),
                ),
            ],
            options={
                "ordering": ["-date_match"],
            },
        ),
        migrations.CreateModel(
            name="ClanMember",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("leader", "Leader"),
                            ("officier", "Officier"),
                            ("membre", "Membre"),
                            ("recrue", "Recrue"),
                        ],
                        default="recrue",
                        max_length=20,
                    ),
                ),
                ("date_rejointe", models.DateTimeField(auto_now_add=True)),
                ("est_actif", models.BooleanField(default=True)),
                (
                    "clan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membres",
                        to="clans_gaming.clan",
                    ),
                ),
                (
                    "gameur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="clans",
                        to="gameurs.gameur",
                    ),
                ),
            ],
            options={
                "ordering": ["-date_rejointe"],
                "unique_together": {("clan", "gameur")},
            },
        ),
    ]

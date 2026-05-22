# Generated manually for the assignment baseline.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LottoRound",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("round_number", models.PositiveIntegerField(unique=True, verbose_name="회차")),
                ("draw_date", models.DateField(verbose_name="추첨일")),
                ("winning_numbers", models.JSONField(blank=True, default=list, verbose_name="당첨 번호")),
                ("bonus_number", models.PositiveIntegerField(blank=True, null=True, verbose_name="보너스 번호")),
                ("is_drawn", models.BooleanField(default=False, verbose_name="추첨 완료")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "로또 회차",
                "verbose_name_plural": "로또 회차",
                "ordering": ["-round_number"],
            },
        ),
        migrations.CreateModel(
            name="LottoTicket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numbers", models.JSONField(verbose_name="구매 번호")),
                (
                    "purchase_type",
                    models.CharField(
                        choices=[("manual", "수동"), ("auto", "자동")],
                        default="manual",
                        max_length=10,
                    ),
                ),
                ("purchased_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "round",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="lotto.lottoround",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "로또 구매 내역",
                "verbose_name_plural": "로또 구매 내역",
                "ordering": ["-purchased_at"],
            },
        ),
        migrations.CreateModel(
            name="LottoResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "rank",
                    models.CharField(
                        choices=[
                            ("1등", "1등"),
                            ("2등", "2등"),
                            ("3등", "3등"),
                            ("4등", "4등"),
                            ("5등", "5등"),
                            ("낙첨", "낙첨"),
                        ],
                        default="낙첨",
                        max_length=10,
                    ),
                ),
                ("match_count", models.PositiveSmallIntegerField(default=0)),
                ("bonus_matched", models.BooleanField(default=False)),
                ("calculated_at", models.DateTimeField(auto_now=True)),
                (
                    "ticket",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="result",
                        to="lotto.lottoticket",
                    ),
                ),
            ],
            options={
                "verbose_name": "당첨 결과",
                "verbose_name_plural": "당첨 결과",
                "ordering": ["ticket__round__round_number", "rank"],
            },
        ),
    ]

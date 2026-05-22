from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from lotto.models import LottoRound


class Command(BaseCommand):
    help = "다음 로또 회차를 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument("--draw-date", help="추첨일을 YYYY-MM-DD 형식으로 지정합니다.")

    def handle(self, *args, **options):
        latest_round = LottoRound.objects.order_by("-round_number").first()
        next_round_number = 1 if latest_round is None else latest_round.round_number + 1
        draw_date = options["draw_date"] or timezone.localdate() + timedelta(days=7)

        lotto_round, created = LottoRound.objects.get_or_create(
            round_number=next_round_number,
            defaults={"draw_date": draw_date},
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"{lotto_round.round_number}회차를 생성했습니다."))
        else:
            self.stdout.write(f"{lotto_round.round_number}회차가 이미 존재합니다.")

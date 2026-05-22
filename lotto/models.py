from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .constants import RANK_CHOICES, RANK_NONE
from .services import evaluate_rank, generate_draw_numbers, validate_lotto_numbers


class LottoRound(models.Model):
    round_number = models.PositiveIntegerField(unique=True, verbose_name="회차")
    draw_date = models.DateField(verbose_name="추첨일")
    winning_numbers = models.JSONField(default=list, blank=True, verbose_name="당첨 번호")
    bonus_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="보너스 번호")
    is_drawn = models.BooleanField(default=False, verbose_name="추첨 완료")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-round_number"]
        verbose_name = "로또 회차"
        verbose_name_plural = "로또 회차"

    def __str__(self):
        return f"{self.round_number}회차"

    def clean(self):
        if self.winning_numbers:
            try:
                validate_lotto_numbers(self.winning_numbers)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc
        if self.bonus_number and not 1 <= self.bonus_number <= 45:
            raise ValidationError("보너스 번호는 1부터 45 사이여야 합니다.")
        if self.bonus_number and self.bonus_number in self.winning_numbers:
            raise ValidationError("보너스 번호는 당첨 번호와 중복될 수 없습니다.")

    def draw(self):
        if self.is_drawn:
            raise ValidationError("이미 추첨이 완료된 회차입니다.")
        self.winning_numbers, self.bonus_number = generate_draw_numbers()
        self.is_drawn = True
        self.full_clean()
        self.save()
        self.calculate_results()

    def calculate_results(self):
        if not self.is_drawn:
            raise ValidationError("추첨 완료 후 당첨 결과를 계산할 수 있습니다.")
        for ticket in self.tickets.select_related("user"):
            rank, match_count, bonus_matched = evaluate_rank(
                ticket.numbers,
                self.winning_numbers,
                self.bonus_number,
            )
            LottoResult.objects.update_or_create(
                ticket=ticket,
                defaults={
                    "rank": rank,
                    "match_count": match_count,
                    "bonus_matched": bonus_matched,
                },
            )


class LottoTicket(models.Model):
    MANUAL = "manual"
    AUTO = "auto"
    PURCHASE_TYPE_CHOICES = [
        (MANUAL, "수동"),
        (AUTO, "자동"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    round = models.ForeignKey(LottoRound, on_delete=models.CASCADE, related_name="tickets")
    numbers = models.JSONField(verbose_name="구매 번호")
    purchase_type = models.CharField(max_length=10, choices=PURCHASE_TYPE_CHOICES, default=MANUAL)
    purchased_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-purchased_at"]
        verbose_name = "로또 구매 내역"
        verbose_name_plural = "로또 구매 내역"

    def __str__(self):
        return f"{self.user} - {self.round} - {self.numbers}"

    def clean(self):
        try:
            self.numbers = validate_lotto_numbers(self.numbers)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        if self.round.is_drawn:
            raise ValidationError("이미 추첨된 회차의 복권은 구매할 수 없습니다.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class LottoResult(models.Model):
    ticket = models.OneToOneField(LottoTicket, on_delete=models.CASCADE, related_name="result")
    rank = models.CharField(max_length=10, choices=RANK_CHOICES, default=RANK_NONE)
    match_count = models.PositiveSmallIntegerField(default=0)
    bonus_matched = models.BooleanField(default=False)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ticket__round__round_number", "rank"]
        verbose_name = "당첨 결과"
        verbose_name_plural = "당첨 결과"

    def __str__(self):
        return f"{self.ticket} - {self.rank}"

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .constants import RANK_FIFTH, RANK_FIRST, RANK_NONE, RANK_SECOND, RANK_THIRD
from .models import LottoResult, LottoRound, LottoTicket
from .services import evaluate_rank, generate_lotto_numbers, validate_lotto_numbers


class LottoServiceTests(TestCase):
    def test_generate_lotto_numbers_returns_six_unique_numbers_in_range(self):
        numbers = generate_lotto_numbers()

        self.assertEqual(len(numbers), 6)
        self.assertEqual(len(set(numbers)), 6)
        self.assertTrue(all(1 <= number <= 45 for number in numbers))

    def test_validate_lotto_numbers_rejects_duplicate_numbers(self):
        with self.assertRaises(ValueError):
            validate_lotto_numbers([1, 1, 2, 3, 4, 5])

    def test_evaluate_rank(self):
        winning_numbers = [1, 2, 3, 4, 5, 6]

        self.assertEqual(evaluate_rank([1, 2, 3, 4, 5, 6], winning_numbers, 7)[0], RANK_FIRST)
        self.assertEqual(evaluate_rank([1, 2, 3, 4, 5, 7], winning_numbers, 7)[0], RANK_SECOND)
        self.assertEqual(evaluate_rank([1, 2, 3, 4, 5, 8], winning_numbers, 7)[0], RANK_THIRD)
        self.assertEqual(evaluate_rank([1, 2, 3, 9, 10, 11], winning_numbers, 7)[0], RANK_FIFTH)
        self.assertEqual(evaluate_rank([1, 2, 9, 10, 11, 12], winning_numbers, 7)[0], RANK_NONE)


class LottoModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password")
        self.round = LottoRound.objects.create(round_number=1, draw_date="2026-05-30")

    def test_manual_ticket_rejects_invalid_numbers(self):
        ticket = LottoTicket(user=self.user, round=self.round, numbers=[1, 2, 3, 4, 5, 50])

        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_draw_calculates_ticket_result(self):
        ticket = LottoTicket.objects.create(
            user=self.user,
            round=self.round,
            numbers=[1, 2, 3, 4, 5, 6],
            purchase_type=LottoTicket.MANUAL,
        )
        self.round.winning_numbers = [1, 2, 3, 4, 5, 6]
        self.round.bonus_number = 7
        self.round.is_drawn = True
        self.round.save()

        self.round.calculate_results()

        result = LottoResult.objects.get(ticket=ticket)
        self.assertEqual(result.rank, RANK_FIRST)
        self.assertEqual(result.match_count, 6)

    def test_ticket_cannot_be_bought_after_draw(self):
        self.round.winning_numbers = [1, 2, 3, 4, 5, 6]
        self.round.bonus_number = 7
        self.round.is_drawn = True
        self.round.save()

        with self.assertRaises(ValidationError):
            LottoTicket.objects.create(
                user=self.user,
                round=self.round,
                numbers=[1, 2, 3, 4, 5, 6],
                purchase_type=LottoTicket.MANUAL,
            )


class LottoViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="password")
        self.staff = User.objects.create_user(username="manager", password="password", is_staff=True)
        self.round = LottoRound.objects.create(round_number=1, draw_date="2026-05-30")

    def test_login_required_for_buy_ticket(self):
        response = self.client.get(reverse("lotto:buy_ticket"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_user_can_buy_manual_ticket(self):
        self.client.login(username="buyer", password="password")

        response = self.client.post(
            reverse("lotto:buy_ticket"),
            {
                "number1": 1,
                "number2": 2,
                "number3": 3,
                "number4": 4,
                "number5": 5,
                "number6": 6,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(LottoTicket.objects.filter(user=self.user, numbers=[1, 2, 3, 4, 5, 6]).exists())

    def test_non_staff_cannot_access_manager_dashboard(self):
        self.client.login(username="buyer", password="password")

        response = self.client.get(reverse("lotto:manager_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_draw_round_from_dashboard(self):
        self.client.login(username="manager", password="password")

        response = self.client.post(reverse("lotto:draw_round", args=[self.round.pk]))

        self.round.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.round.is_drawn)
        self.assertEqual(len(self.round.winning_numbers), 6)
        self.assertIsNotNone(self.round.bonus_number)

import random

from .constants import (
    LOTTO_MAX_NUMBER,
    LOTTO_MIN_NUMBER,
    LOTTO_PICK_COUNT,
    RANK_FIRST,
    RANK_FIFTH,
    RANK_FOURTH,
    RANK_NONE,
    RANK_SECOND,
    RANK_THIRD,
)


def normalize_numbers(numbers):
    return sorted(int(number) for number in numbers)


def validate_lotto_numbers(numbers):
    normalized = normalize_numbers(numbers)
    if len(normalized) != LOTTO_PICK_COUNT:
        raise ValueError("로또 번호는 6개여야 합니다.")
    if len(set(normalized)) != LOTTO_PICK_COUNT:
        raise ValueError("로또 번호는 중복될 수 없습니다.")
    if any(number < LOTTO_MIN_NUMBER or number > LOTTO_MAX_NUMBER for number in normalized):
        raise ValueError("로또 번호는 1부터 45 사이여야 합니다.")
    return normalized


def generate_lotto_numbers():
    return sorted(random.sample(range(LOTTO_MIN_NUMBER, LOTTO_MAX_NUMBER + 1), LOTTO_PICK_COUNT))


def generate_draw_numbers():
    numbers = random.sample(range(LOTTO_MIN_NUMBER, LOTTO_MAX_NUMBER + 1), LOTTO_PICK_COUNT + 1)
    return sorted(numbers[:LOTTO_PICK_COUNT]), numbers[-1]


def evaluate_rank(ticket_numbers, winning_numbers, bonus_number):
    ticket_numbers = set(validate_lotto_numbers(ticket_numbers))
    winning_numbers = set(validate_lotto_numbers(winning_numbers))
    match_count = len(ticket_numbers & winning_numbers)
    bonus_matched = int(bonus_number) in ticket_numbers

    if match_count == 6:
        rank = RANK_FIRST
    elif match_count == 5 and bonus_matched:
        rank = RANK_SECOND
    elif match_count == 5:
        rank = RANK_THIRD
    elif match_count == 4:
        rank = RANK_FOURTH
    elif match_count == 3:
        rank = RANK_FIFTH
    else:
        rank = RANK_NONE

    return rank, match_count, bonus_matched

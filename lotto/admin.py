from django.contrib import admin

from .models import LottoResult, LottoRound, LottoTicket


@admin.register(LottoRound)
class LottoRoundAdmin(admin.ModelAdmin):
    list_display = ("round_number", "draw_date", "winning_numbers", "bonus_number", "is_drawn")
    list_filter = ("is_drawn",)
    search_fields = ("round_number",)
    actions = ("draw_selected_rounds",)

    @admin.action(description="선택한 회차 추첨 실행")
    def draw_selected_rounds(self, request, queryset):
        for lotto_round in queryset:
            lotto_round.draw()


@admin.register(LottoTicket)
class LottoTicketAdmin(admin.ModelAdmin):
    list_display = ("user", "round", "numbers", "purchase_type", "purchased_at")
    list_filter = ("purchase_type", "round")
    search_fields = ("user__username", "round__round_number")


@admin.register(LottoResult)
class LottoResultAdmin(admin.ModelAdmin):
    list_display = ("ticket", "rank", "match_count", "bonus_matched", "calculated_at")
    list_filter = ("rank", "bonus_matched", "ticket__round")
    search_fields = ("ticket__user__username",)

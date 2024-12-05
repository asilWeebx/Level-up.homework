from django.contrib import admin
from .models import Profile, Unit, Question, Result, Level, UserAnswer, Presents,Claim

# Profile modelini admin paneliga qo'shish
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'level', 'coins')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('level',)

# Level modelini admin paneliga qo'shish
@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)

# Unit modelini admin paneliga qo'shish
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('title', 'level')
    search_fields = ('title',)
    list_filter = ('level',)

# Question modelini admin paneliga qo'shish
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'unit', 'correct_answer')
    search_fields = ('question_text',)
    list_filter = ('unit',)

# Result modelini admin paneliga qo'shish
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit', 'score', 'level')
    search_fields = ('student__user__username',)
    list_filter = ('unit', 'level')

# UserAnswer modelini admin paneliga qo'shish
@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'answer', 'correct')
    search_fields = ('user__username', 'question__question_text')
    list_filter = ('correct',)


admin.site.register(Presents)
admin.site.register(Claim)
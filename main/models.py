from django.db import models
from django.contrib.auth.models import User


class Level(models.Model):
    """Darajalar modeli."""
    title = models.CharField(max_length=50)  # Masalan: Beginner, Elementary
    description = models.TextField(null=True, blank=True)  # Daraja haqida qisqacha tavsif
    order = models.PositiveIntegerField(unique=True)  # Tartibni belgilash uchun
    def __str__(self):
        return self.title


class Profile(models.Model):
    """Foydalanuvchi profili modeli."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    level = models.ForeignKey(Level, on_delete=models.SET_DEFAULT, default=1)  # Daraja bilan bog'lanadi
    coins = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username


class Unit(models.Model):
    """Unitlar darajalar bilan bog'lanadi."""
    title = models.CharField(max_length=255)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)  # Unit darajasi

    def __str__(self):
        return f"{self.title} ({self.level.title})"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('text', 'Matnli javob'),
        ('choice', 'Variantli javob (A, B, C, D)'),
    ]
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    question_text = models.TextField()  # Savol matni
    question_type = models.CharField(
        max_length=10, 
        choices=QUESTION_TYPE_CHOICES, 
        default='text'
    )  # Savol turi
    image = models.ImageField(upload_to='questions/', blank=True, null=True)  # Ixtiyoriy rasm
    has_image = models.BooleanField(default=False)  # Agar true bo'lsa, savolga rasm kerak
    """Savollarni saqlash."""
    # Variantlar uchun choices
    option_a = models.CharField(max_length=255, blank=True, null=True)  # A varianti
    option_b = models.CharField(max_length=255, blank=True, null=True)  # B varianti
    option_c = models.CharField(max_length=255, blank=True, null=True)  # C varianti
    option_d = models.CharField(max_length=255, blank=True, null=True)  # D varianti
    correct_answer = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="To'g'ri javob ('text' turi uchun matn, 'choice' uchun A, B, C yoki D)"
    )  # To'g'ri javob

    def __str__(self):
        return f"Question for {self.unit.title}"

class Result(models.Model):
    """Talabaning unit bo'yicha natijalari."""
    student = models.ForeignKey(Profile, on_delete=models.CASCADE)  # Talaba
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)  # Unit
    score = models.PositiveIntegerField()  # Talabaning foiz ko'rinishidagi natijasi (0-100%)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)  # Natijani olish paytidagi daraja
    coins_given = models.BooleanField(default=False)  # Coin berilganini saqlash uchun
    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name} - {self.unit.title} - {self.level.title}"

    def save(self, *args, **kwargs):
        """Unitni 100% bajarilganda 1 tanga berish."""
        if self.score == 100:
            self.student.coins += 1
            self.student.save()
        super().save(*args, **kwargs)


class UserAnswer(models.Model):
    """Foydalanuvchi javoblari."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=250, null=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.question.question_text}"


class Presents(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return f"{self.name}"
    
class Claim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Presents, on_delete=models.CASCADE)
    claimed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Claim by {self.user.username} - {self.reward.name}"

import time
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import  UserCreationForm,AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Unit, Question, Result, UserAnswer, Level, Presents, Claim
from django.http import HttpResponse,HttpResponseNotAllowed
from .forms import CustomUserCreationForm
from django.contrib.auth import logout
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Unit, Profile, Result, UserAnswer
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .EmailBackEnd import EmailBackEnd

from django.http import JsonResponse

def Logout(request):
    logout(request)
    return redirect('logout_page')

def logout_page(request):
    return render(request,'registration/logged_out.html')
# Register view
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Profile for the newly registered user
            profile = Profile(user=user, level=form.cleaned_data['level'])
            profile.save()
            return redirect('login')  # Redirect to login after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Agar superuser bo'lsa, maxsus sahifaga yo'naltirish
            login(request, user)
            return redirect('home')  # Oddiy foydalanuvchi uchun sahifa
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
# Home page view
@login_required
def home(request):
    user_profile = Profile.objects.get(user=request.user)
    profile = Profile.objects.get(user=request.user)
    units = Unit.objects.filter(level=profile.level)  # Show units based on the user's level
 
   
    ctx = {
        'coins': user_profile.coins,         # Foydalanuvchi coins miqdori
        'user_profile': user_profile,
        'profile':profile,
        'units': units
    }
    return render(request, 'home.html',ctx)

# Units page view - Shows all units for the selected level
@login_required
def units(request):
    profile = Profile.objects.get(user=request.user)
    units = Unit.objects.filter(level=profile.level)  # Only show units for the current level
    return render(request, 'units.html', {'units': units})


def units_detail(request, unit_id):
    try:
        unit = Unit.objects.get(id=unit_id)
        questions = unit.question_set.all()  # Unitga tegishli savollar
    except Unit.DoesNotExist:
        raise Http404("Unit not found")

    user_profile = Profile.objects.get(user=request.user)

    # Resultni olish yoki yangi yaratish
    result, created = Result.objects.get_or_create(
        student=user_profile,
        unit=unit,
        defaults={'level': unit.level, 'score': 0, 'coins_given': False}
    )

    question_index = request.GET.get('question', 0)
    question_index = int(question_index)

    # Agar barcha savollar yechilgan bo'lsa, `my_results` sahifasiga yo'naltirish
    if question_index >= len(questions):
        # 100% to'g'ri javob bo'lsa, coin berish
        if result.score == len(questions):  # Coins only given if not given before
            user_profile.coins += 1
            user_profile.save()
            result.save()
        
        # Natijalar sahifasiga yo'naltirish
        return redirect('my_results')  # `my_results` sahifasiga yo'naltirish

    if question_index < len(questions):
        question = questions[question_index]
    else:
       return redirect('my_results')  # Tugagan bo'lsa yo'naltirish

    if request.method == 'POST':
        user_answer = request.POST.get('answer').strip().lower()
        correct = user_answer == question.correct_answer.strip().lower()  # Javob to'g'ri yoki noto'g'ri

        # Javobni saqlash
        existing_answer = UserAnswer.objects.filter(user=request.user, question=question).first()

        if existing_answer:
            # Agar foydalanuvchi oldin javob bergan bo'lsa
            if existing_answer.correct:
                # Agar oldingi javob to'g'ri bo'lsa, progress oshirmaslik
                return JsonResponse({'correct': correct, 'next_question_index': question_index + 1})
            else:
                # Agar oldingi javob noto'g'ri bo'lsa, progressni oshirish
                if correct:  # Faqat to'g'ri javob bo'lsa progressni oshiramiz
                    result.score += 1
                    result.save()
                existing_answer.answer = user_answer  # Javobni yangilash
                existing_answer.correct = correct
                existing_answer.save()
                return JsonResponse({'correct': correct, 'next_question_index': question_index + 1})
        else:
            # Agar foydalanuvchi birinchi marta javob berayotgan bo'lsa
            UserAnswer.objects.create(user=request.user, question=question, answer=user_answer, correct=correct)

            if correct:
                result.score += 1
                result.save()

        next_question_index = question_index + 1
        return JsonResponse({'correct': correct, 'next_question_index': next_question_index})

    # Savolni ko'rsatish
    return render(request, 'unit_detail.html', {
        'unit': unit,
        'question': question,
        'question_index': question_index,
        'time_limit': timezone.now() + timezone.timedelta(seconds=30),  # 30 soniya cheklov
    })

def submit_answers(request, unit_id, question_id):
    # Savolni olish
    question = Question.objects.get(id=question_id)
    unit = question.unit  # Savol qaysi unitga tegishli ekanini aniqlash
    user_profile = Profile.objects.get(user=request.user)

    # Vaqtni tekshirish
    question_time_limit = timezone.now() - timezone.timedelta(seconds=30)
    
    # Foydalanuvchi javobini olish
    if request.method == 'POST':
        user_answer = request.POST.get('answer')
        correct = user_answer == question.correct_answer  # To'g'ri yoki noto'g'ri javob

        # Javobni saqlash
        UserAnswer.objects.create(
            user=request.user,
            question=question,
            answer=user_answer,
            correct=correct,
        )

        # Natijalarni saqlash
        result, created = Result.objects.get_or_create(student=user_profile, unit=unit)
        if correct:
            result.score += 1
        result.save()

        # Keyingi savolga o'tish
        return redirect('next_question', unit_id=unit.id, question_id=question_id + 1)

    # Vaqt tugasa javobni avtomatik tarzda tekshirish
    if request.user in question.time_answers and question.time_answers[request.user] < question_time_limit:
        return redirect('next_question', unit_id=unit.id, question_id=question_id + 1)

    return render(request, 'question_view.html', {'question': question})

# Get the next level
def get_next_level(current_level):
    # Get the list of levels ordered
    level_order = ['Beginner', 'Elementry', 'Pre-Intermediate', 'Intermediate']
    try:
        current_index = level_order.index(current_level)
        next_index = current_index + 1
        if next_index < len(level_order):
            return Level.objects.get(title=level_order[next_index])  # Get the next level object
        else:
            return None
    except ValueError:
        return None
from django.db.models import Sum

def check_level_progress(user_profile):
    # Joriy darajadagi barcha unitlarni olish
    current_level = user_profile.level
    units_in_level = Unit.objects.filter(level=current_level)

    if not units_in_level.exists():  # Agar unit mavjud bo'lmasa
        return 0

    total_units = units_in_level.count()  # Jami unitlar soni

    # Foydalanuvchining har bir unit bo'yicha progressini hisoblash
    completed_units = 0

    for unit in units_in_level:
        total_questions = unit.question_set.count()  # Har bir unitdagi savollar soni
        if total_questions == 0:  # Agar unitda savol bo'lmasa, unitni hisobga olmaslik
            continue

        # Foydalanuvchining ushbu unitdagi to'plagan ballari
        unit_score = Result.objects.filter(student=user_profile, unit=unit).aggregate(Sum('score'))['score__sum'] or 0

        # Agar unit progressi 70% yoki undan yuqori bo'lsa, bu unitni "bajarilgan" deb hisoblaymiz
        if (unit_score / total_questions) * 100 >= 70:
            completed_units += 1

    # Umumiy progress: Bajarilgan unitlar / jami unitlar
    overall_progress = (completed_units / total_units) * 100

    # Agar umumiy progress 70% yoki undan yuqori bo'lsa, keyingi darajaga o'tkazish
    if overall_progress >= 70:
        next_level = Level.objects.filter(order=current_level.order + 1).first()
        if next_level:
            user_profile.level = next_level
            user_profile.save()
# Foizni ikki onlik raqam bilan formatlash
    overall_progress = round(overall_progress, 1)
    return overall_progress

@login_required
def my_results(request):
    user_profile = Profile.objects.get(user=request.user)
    progress = check_level_progress(user_profile)  # Progressni hisoblash
    resultss = Result.objects.filter(student=user_profile)  # Foydalanuvchining barcha natijalari
     # Foydalanuvchi profili

    # Foydalanuvchining barcha natijalari
    results = Result.objects.filter(student=user_profile).select_related('unit', 'level')

    # Daraja bo'yicha natijalarni guruhlash
    results_by_level = {}
    for result in results:
        level = result.level.title  # Darajaning nomi
        if level not in results_by_level:
            results_by_level[level] = []
        results_by_level[level].append({
            'unit': result.unit.title,  # Unit nomi
            'score': result.score,      # Unitdagi ball
            'total_questions': result.unit.question_set.count()  # Savollar soni
        })

    # Ma'lumotlarni kontekstga qo'shish
    ctx = {
        'coins': user_profile.coins,         # Foydalanuvchi coins miqdori
        'results_by_level': results_by_level,  # Daraja bo'yicha natijalar
        'progress': progress,
        'results': resultss,
        'user_profile': user_profile,
    }
    return render(request, 'my_results.html', ctx)



def rewards(request):
    user_profile = Profile.objects.get(user=request.user)
    rewards = Presents.objects.all()

    ctx = {
         'coins': user_profile.coins,         # Foydalanuvchi coins miqdori
        "rewards": rewards
    }

    return render(request,'rewards.html',ctx)




@login_required
def update_settings(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        # Ma'lumotlarni yangilash
        user.first_name = first_name
        user.last_name = last_name
        user.profile.phone = phone

        # Parolni tasdiqlash va yangilash
        if password:
            if password == confirm_password:
                user.set_password(password)
                messages.success(request, "Parol muvaffaqiyatli o'zgartirildi.")
            else:
                messages.error(request, "Parol tasdiqlash noto'g'ri.")
                return redirect('update_settings')

        user.save()
        user.profile.save()
        messages.success(request, "Sozlamalar muvaffaqiyatli yangilandi.")
        return redirect('update_settings')

    return render(request, 'settings.html', {'user': request.user})


def claim_reward(request, reward_id):
    reward = get_object_or_404(Presents, id=reward_id)
    profile = request.user.profile  # Foydalanuvchi profili

    if profile.coins >= reward.price:
        # Tasdiqlash: Haqiqatan ham sotib olmoqchimi?
        if request.method == "POST":
            # Coinlarni kamaytirish
            profile.coins -= reward.price
            profile.save()

            # Chek yaratish
            Claim.objects.create(user=request.user, reward=reward)

            messages.success(request, f"{reward.name} muvaffaqiyatli sotib olindi!")
            return redirect('rewards')

        return render(request, 'confirm_claim.html', {'reward': reward})
    else:
        messages.error(request, "Yetarli coins mavjud emas.")
        return redirect('rewards')
    
def my_rewards(request):
    # Foydalanuvchining sovg'alarini olish
    if request.user.is_authenticated:
        rewards = Claim.objects.filter(user=request.user)
    else:
        rewards = None
     
    
    return render(request, 'my_rewards.html', {'rewards': rewards})

def doLogin(request):
        if request.method == "POST":
            user = EmailBackEnd.authenticate(request, username=request.POST.get('username'),
                                             password=request.POST.get('password'))
            if user != None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, 'ADMIN DASHBOARDGA MARHAMAT')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Siz SuperUser emassiz!')
                    return redirect('loginn')
            else:
                messages.error(request, 'Parol yoki Username Xato!')
                return redirect('loginn')

        return None

def LOGINN(request):
    return render(request, 'dashboard/login.html')


def admin_dashboard(request):
    if request.user.is_active:
        total_students = Profile.objects.count()  # Jami talabalar
        completed_students = Profile.objects.filter(level__isnull=False).count()  # Daraja bajargan talabalar

        # Har bir daraja bo'yicha talabalar soni
        beginner_count = Profile.objects.filter(level="1").count()
        elementary_count = Profile.objects.filter(level="2").count()
        intermediate_count = Profile.objects.filter(level="3").count()
        advanced_count = Profile.objects.filter(level="4").count()

        return render(request, 'dashboard/admin_dashboard.html', {
            'total_students': total_students,
            'completed_students': completed_students,
            'beginner_count': beginner_count,
            'elementary_count': elementary_count,
            'intermediate_count': intermediate_count,
            'advanced_count': advanced_count,
        })
            
    else:
       messages.error(request, 'Siz SuperUser emassiz!')
       return redirect('loginn')

from django.shortcuts import render
from .models import Profile, Result

def view_students(request):
    search_query = request.GET.get('search', '')  # URL parametridan qidiruv so'rovini olish
    students = Profile.objects.all()
    
    if search_query:
        # Qidiruvga mos talabalarni topish (username, first_name, last_name bo'yicha)
        students = students.filter(
            user__username__icontains=search_query
        ) | students.filter(
            user__first_name__icontains=search_query
        ) | students.filter(
            user__last_name__icontains=search_query
        )

    student_info = []
    for student in students:
        # Talabaning oxirgi darajasi va natijalarini olish
        current_result = Result.objects.filter(student=student).last()
        student_info.append({
            'student': student,
            'current_level': current_result.level if current_result else "No Levels Completed"
        })

    ctx = {
        'student_info': student_info,
    }
    return render(request, 'dashboard/view_students.html', ctx)


def view_student_levels(request, student_id):
    try:
        student = Profile.objects.get(id=student_id)
        results = Result.objects.filter(student=student)
        
        # Noyob darajalarni olish uchun Python orqali filtrlash
        unique_levels = {}
        for result in results:
            if result.level.id not in unique_levels:
                unique_levels[result.level.id] = result.level

    except Profile.DoesNotExist:
        return HttpResponse("Student not found.", status=404)

    context = {
        'student': student,
        'results': unique_levels.values(),  # Faqat noyob darajalarni ko'rsatish
    }
    return render(request, 'dashboard/view_student_levels.html', context)

def view_level_units(request, level_id, student_id):
    level = get_object_or_404(Level, id=level_id)
    student = get_object_or_404(Profile, id=student_id)

    # Ushbu darajadagi unitlarni olish
    units = Unit.objects.filter(level=level)
    unit_results = []

    for unit in units:
        result = Result.objects.filter(student=student, unit=unit).first()
        if result:
            unit_results.append({'unit': unit, 'result': result})

    return render(request, 'dashboard/view_level_units.html', {'level': level, 'unit_results': unit_results, 'student': student})

def view_unit_questions(request, unit_id, student_id):
    unit = get_object_or_404(Unit, id=unit_id)
    student = get_object_or_404(Profile, id=student_id)

    # Unit savollari va foydalanuvchi javoblari
    questions = unit.question_set.all()
    question_details = []

    for question in questions:
        user_answer = UserAnswer.objects.filter(user=student.user, question=question).first()
        question_details.append({
            'question': question,
            'user_answer': user_answer.answer if user_answer else "No Answer",
            'correct': user_answer.correct if user_answer else False
        })

    return render(request, 'dashboard/view_unit_questions.html', {
        'unit': unit,
        'student': student,
        'question_details': question_details
    })


def view_question(request, unit_id, question_id, student_id):
    unit = get_object_or_404(Unit, id=unit_id)
    question = get_object_or_404(Question, id=question_id)
    student = get_object_or_404(Profile, id=student_id)

    user_answer = UserAnswer.objects.filter(user=student.user, question=question).first()

    return render(request, 'dashboard/view_question_details.html', {
        'unit': unit,
        'question': question,
        'student': student,
        'user_answer': user_answer,
    })


from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from .views import Logout,logout_page,update_settings,rewards,my_rewards,admin_dashboard,LOGINN,doLogin
urlpatterns = [
    # Register and Login URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/profile/',views.home,name='home'),
    # Home page (dashboard)
    path('', views.home, name='home'),
    path('rewards/claim/<int:reward_id>/', views.claim_reward, name='claim_reward'),
    path('question/<int:unit_id>/<int:question_id>/', views.submit_answers, name='submit_answers'),
    # Units page - list all units for the selected level
    path('units/', views.units, name='units'),
    path('logout_page',logout_page,name='logout_page'),
    # Unit detail page (questions for the selected unit)
    path('units/<int:unit_id>/', views.units_detail, name='unit_detail'),
    path('rewards/',rewards,name='rewards'),
    # Submit answers for a unit
    path('submit_answers/<int:unit_id>/', views.submit_answers, name='submit_answers'),
    # My results page - shows all results for the logged-in user
    path('my_results/', views.my_results, name='my_results'),
    path('accounts/', include('django.contrib.auth.urls')),  # Login, logout, password change u
    path('logout_user/', Logout,name='logout'),
    path('settings/',update_settings,name='update_settings'),
    path('my_rewards/',my_rewards,name='my_rewards'),
    path('admin_dashboard/',admin_dashboard,name="admin_dashboard"),
    path('doLogin/', doLogin, name='doLogin'),
    path('admin_login/',LOGINN,name="loginn"),
    path('students_view/',views.view_students,name="student_list"),
    path('student/<int:student_id>/levels/', views.view_student_levels, name='view_student_levels'),
    path('student/<int:student_id>/level/<int:level_id>/units/', views.view_level_units, name='view_level_units'),
    path('unit/<int:unit_id>/question/<int:question_id>/student/<int:student_id>/', views.view_question, name='view_question'),
    path('student/<int:student_id>/unit/<int:unit_id>/questions/', views.view_unit_questions, name='view_unit_questions'),
     path('students/', views.view_students, name='view_students'),
]
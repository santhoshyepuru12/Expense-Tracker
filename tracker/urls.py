from django.urls import path
from . import views

urlpatterns = [

    # Home
    path("", views.home, name="home"),

    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),

    # Register
    path("register/", views.register, name="register"),

    # Login      # Username Login (POST)

    path("login/", views.login_user, name="login") ,
    
    path("register/verify/",views.verify_register_otp,name="verify_register_otp"),      
    
    path("login/username/", views.login_user, name="username_login"),

    path("login/email/", views.request_otp, name="request_otp"),

    path("login/verify/", views.verify_otp, name="verify_otp"),

    path("logout/", views.logout_user, name="logout"),

    # Expenses
    path("expenses/", views.expense_list, name="expense_list"),

    path("add/", views.add_expense, name="add_expense"),

    path("edit/<int:id>/", views.edit_expense, name="edit_expense"),

    path("delete/<int:id>/", views.delete_expense, name="delete_expense"),

    # Reports
    path("monthly-report/", views.monthly_report, name="monthly_report"),

    path("monthly-report/pdf/",views.export_monthly_pdf,name="export_monthly_pdf"),

    path( "monthly-report/excel/", views.export_monthly_excel, name="export_monthly_excel"),

    # Budget
    path("set-budget/", views.set_budget, name="set_budget"),

    # Profile
    path("profile/", views.profile, name="profile"),

    path("profile/send-password-otp/",views.send_password_otp,name="send_password_otp"),

    path( "profile/verify-password-otp/",views.verify_password_otp,name="verify_password_otp"),

    path("profile/change-password/",views.change_password,name="change_password")
]
import random
import secrets
from django.utils import timezone
from datetime import timedelta
from threading import Thread
from django.core.mail import send_mail,EmailMultiAlternatives
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from openpyxl import Workbook
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum, Max, Min
from .models import Expense,Budget
from .forms import ExpenseForm, RegisterForm,BudgetForm,UpdateProfileForm
from datetime import date
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.dateparse import parse_datetime
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm



def home(request):

    username_form = AuthenticationForm()

    return render(
        request,
        "index.html",
        {
            "username_form": username_form,
        },
    )

@login_required
def add_expense(request):

    if request.method == "POST":

        form = ExpenseForm(request.POST)

        if form.is_valid():

            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense Added Successfully!")
            return redirect("/expenses/")

    else:

        form = ExpenseForm()

    return render(request, "add_expense.html", {"form": form})


@login_required
def expense_list(request):

    expenses = Expense.objects.filter(
        user=request.user
    ).order_by("-date")

    search = request.GET.get("search")
    category = request.GET.get("category")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if search:
        expenses = expenses.filter(title__icontains=search)

    if category:
        expenses = expenses.filter(category=category)

    if from_date:
        expenses = expenses.filter(date__gte=from_date)

    if to_date:
        expenses = expenses.filter(date__lte=to_date)

    paginator = Paginator(expenses, 10)

    page_number = request.GET.get("page")

    expenses = paginator.get_page(page_number)

    return render(request, "expense_list.html", {
        "expenses": expenses
    })


@login_required
def edit_expense(request, id):

    expense = get_object_or_404(
        Expense,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        form = ExpenseForm(request.POST, instance=expense)

        if form.is_valid():

            updated_expense = form.save(commit=False)
            updated_expense.user = request.user
            updated_expense.save()
            messages.success(request, "Expense Updated Successfully!")
            return redirect("/expenses/")

    else:

        form = ExpenseForm(instance=expense)

    return render(request, "edit_expense.html", {
        "form": form
    })


@login_required
def delete_expense(request, id):

    expense = get_object_or_404(
        Expense,
        id=id,
        user=request.user
    )

    expense.delete()
    messages.success(request, "Expense Deleted Successfully!")
    return redirect("/expenses/")


@login_required
def dashboard(request):

    user_expenses = Expense.objects.filter(user=request.user)
    from datetime import date

    today = date.today()

    current_month_expenses = user_expenses.filter(
        date__year=today.year,
        date__month=today.month
    )

    current_month_spent = current_month_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    current_budget = Budget.objects.filter(
        user=request.user,
        month__year=today.year,
        month__month=today.month
    ).first()

    budget_amount = current_budget.amount if current_budget else 0

    remaining_budget = budget_amount - current_month_spent

    if budget_amount > 0:
        budget_percentage = (
            float(current_month_spent) /
            float(budget_amount)
        ) * 100
    else:
        budget_percentage = 0

    progress_percentage = min(budget_percentage, 100)

    if budget_amount == 0:
        budget_status = "no_budget"
    elif current_month_spent > budget_amount:
        budget_status = "exceeded"
    elif budget_percentage >= 80:
        budget_status = "warning"
    else:
        budget_status = "safe"

    total_expense = user_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_transactions = user_expenses.count()

    highest_expense = user_expenses.aggregate(
        highest=Max("amount")
    )["highest"] or 0

    lowest_expense = user_expenses.aggregate(
        lowest=Min("amount")
    )["lowest"] or 0

    latest_expenses = user_expenses.order_by("-date")[:5]

    food = user_expenses.filter(
        category="Food"
    ).aggregate(total=Sum("amount"))["total"] or 0

    travel = user_expenses.filter(
        category="Travel"
    ).aggregate(total=Sum("amount"))["total"] or 0

    shopping = user_expenses.filter(
        category="Shopping"
    ).aggregate(total=Sum("amount"))["total"] or 0

    bills = user_expenses.filter(
        category="Bills"
    ).aggregate(total=Sum("amount"))["total"] or 0

    entertainment = user_expenses.filter(
        category="Entertainment"
    ).aggregate(total=Sum("amount"))["total"] or 0

    medical = user_expenses.filter(
        category="Medical"
    ).aggregate(total=Sum("amount"))["total"] or 0

    others = user_expenses.filter(
        category="Others"
    ).aggregate(total=Sum("amount"))["total"] or 0

    monthly_data = (
    user_expenses
    .annotate(month=TruncMonth("date"))
    .values("month")
    .annotate(total=Sum("amount"))
    .order_by("month")
    )

    monthly_labels = [
        item["month"].strftime("%b %Y")
        for item in monthly_data
    ]

    monthly_values = [
        float(item["total"])
        for item in monthly_data
    ]
        # Smart Spending Insights

    today = date.today()

    # Current month expenses
    this_month_expenses = user_expenses.filter(
        date__year=today.year,
        date__month=today.month
    )

    this_month_total = this_month_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0


    # Previous month calculation
    if today.month == 1:
        previous_month = 12
        previous_year = today.year - 1
    else:
        previous_month = today.month - 1
        previous_year = today.year


    # Previous month expenses
    previous_month_expenses = user_expenses.filter(
        date__year=previous_year,
        date__month=previous_month
    )

    previous_month_total = previous_month_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0


    # Find highest spending category this month
    highest_category_data = (
        this_month_expenses
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
        .first()
    )

    if highest_category_data:
        highest_category = highest_category_data["category"]
        highest_category_amount = highest_category_data["total"]
    else:
        highest_category = "No expenses"
        highest_category_amount = 0


    # Compare current month with previous month
    if previous_month_total > 0:

        spending_change = (
            (float(this_month_total) - float(previous_month_total))
            / float(previous_month_total)
        ) * 100

        if spending_change > 0:
            spending_trend = "increased"

        elif spending_change < 0:
            spending_trend = "decreased"

        else:
            spending_trend = "same"

    else:
        spending_change = 0
        spending_trend = "no_previous_data"
    
    context = {
        "total_expense": total_expense,
        "total_transactions": total_transactions,
        "highest_expense": highest_expense,
        "lowest_expense": lowest_expense,
        "latest_expenses": latest_expenses,
        "food": food,
        "travel": travel,
        "shopping": shopping,
        "bills": bills,
        "entertainment": entertainment,
        "medical": medical,
        "others": others,
        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,
        "budget_amount": budget_amount,
        "current_month_spent": current_month_spent,
        "remaining_budget": remaining_budget,
        "budget_percentage": round(budget_percentage, 1),
        "progress_percentage": progress_percentage,
        "budget_status": budget_status,
        "this_month_total": this_month_total,
        "previous_month_total": previous_month_total,
        "highest_category": highest_category,
        "highest_category_amount": highest_category_amount,
        "spending_change": round(abs(spending_change), 1),
        "spending_trend": spending_trend,
    }

    return render(request, "dashboard.html", context)


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            otp = random.randint(100000, 999999)

            request.session["register_otp"] = str(otp)

            request.session["register_data"] = {
                "first_name": form.cleaned_data["first_name"],
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "password": form.cleaned_data["password1"],
            }

            Thread(
                target=send_otp_email,
                args=(form.cleaned_data["email"], otp),
                daemon=True,
            ).start()

            messages.success(
                request,
                "OTP sent to your email."
            )

            return render(
                request,
                "register.html",
                {
                    "show_verify": True,
                    "email": form.cleaned_data["email"],
                    "verify_type": "register",
                },
            )

    else:

        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form
        }
    )


def login_user(request):

    if request.method != "POST":
        return redirect("home")

    form = AuthenticationForm(request, data=request.POST)

    if form.is_valid():

        login(request, form.get_user())

        messages.success(request, "Welcome back!")

        return redirect("dashboard")

    username_form = AuthenticationForm()

    return render(
        request,
        "index.html",
        {
            "username_form": username_form,
            "show_username": True,
        },
    )


def logout_user(request):

    logout(request)
    messages.success(request, "Logged Out Successfully!")
    return redirect("/login/")


@login_required
def monthly_report(request):

    user_expenses = Expense.objects.filter(
        user=request.user
    )

    month = request.GET.get("month")

    if month:

        year, month_number = month.split("-")

        user_expenses = user_expenses.filter(
            date__year=year,
            date__month=month_number
        )

    user_expenses = user_expenses.order_by("-date")

    total_expense = user_expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_transactions = user_expenses.count()

    highest_expense = user_expenses.aggregate(
        highest=Max("amount")
    )["highest"] or 0

    lowest_expense = user_expenses.aggregate(
        lowest=Min("amount")
    )["lowest"] or 0

    context = {
        "expenses": user_expenses,
        "total_expense": total_expense,
        "total_transactions": total_transactions,
        "highest_expense": highest_expense,
        "lowest_expense": lowest_expense,
        "selected_month": month,
    }

    return render(
        request,
        "monthly_report.html",
        context
    )



@login_required
def export_monthly_pdf(request):

    month = request.GET.get("month")
    expenses = Expense.objects.filter( user=request.user).order_by("-date")
    if month:
        year, month_number = month.split("-")
        expenses = expenses.filter(date__year=year,date__month=month_number)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = ('attachment; filename="monthly_expense_report.pdf"' )
    pdf = canvas.Canvas(response)
    pdf.setTitle("Monthly Expense Report")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180,800,"Monthly Expense Report")
    pdf.setFont("Helvetica", 12)
    if month:
        pdf.drawString(50,770, f"Month: {month}")
    y = 730
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, y, "Title")
    pdf.drawString(200, y, "Category")
    pdf.drawString(330, y, "Amount")
    pdf.drawString(430, y, "Date")
    y -= 25
    pdf.setFont("Helvetica", 10)
    for expense in expenses:

        pdf.drawString(50,y, str(expense.title))
        pdf.drawString(200,y,str(expense.category))
        pdf.drawString(330, y,f"Rs. {expense.amount}")
        pdf.drawString(430, y, str(expense.date))
        y -= 25
        if y < 50:
            pdf.showPage()
            y = 800
    pdf.save()
    return response


@login_required
def export_monthly_excel(request):

    month = request.GET.get("month")

    expenses = Expense.objects.filter(
        user=request.user
    ).order_by("-date")

    if month:
        year, month_number = month.split("-")

        expenses = expenses.filter(
            date__year=year,
            date__month=month_number
        )

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Monthly Expenses"

    worksheet.append([
        "Title",
        "Category",
        "Amount",
        "Date"
    ])

    for expense in expenses:

        worksheet.append([
            expense.title,
            expense.category,
            float(expense.amount),
            expense.date
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = (
        'attachment; filename="monthly_expense_report.xlsx"'
    )

    workbook.save(response)

    return response


@login_required
def set_budget(request):

    if request.method == "POST":
        form = BudgetForm(request.POST)

        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user

            existing_budget = Budget.objects.filter(
                user=request.user,
                month__year=budget.month.year,
                month__month=budget.month.month
            ).first()

            if existing_budget:
                existing_budget.amount = budget.amount
                existing_budget.save()

                messages.success(
                    request,
                    "Monthly budget updated successfully!"
                )
            else:
                budget.save()

                messages.success(
                    request,
                    "Monthly budget set successfully!"
                )

            return redirect("/dashboard/")

    else:
        form = BudgetForm()

    return render(
        request,
        "set_budget.html",
        {"form": form}
    )

def send_otp_email(email, otp):

    subject = "Expense Tracker - Login Verification"

    context = {
        "otp": otp,
    }

    html_message = render_to_string(
        "emails/otp_email.html",
        context
    )

    message = EmailMultiAlternatives(
        subject,
        f"Your OTP is {otp}",
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )

    message.attach_alternative(html_message, "text/html")

    message.send()



def request_otp(request):

    if request.method != "POST":
        return redirect("home")

    email = request.POST.get("email")

    if not email:

        messages.error(request, "Please enter your email.")

        return redirect("home")

    try:

        user = User.objects.get(email=email)

    except User.DoesNotExist:

        messages.error(request, "Email not registered.")

        return redirect("home")

    otp = random.randint(100000, 999999)

    request.session["otp"] = str(otp)
    request.session["otp_email"] = email

    Thread(
    target=send_otp_email,
    args=(email, otp),
    daemon=True,).start()

    username_form = AuthenticationForm()

    return render(
        request,
        "index.html",
        {
            "username_form": username_form,
            "show_verify": True,
            "email": email,
        },
    )


def verify_otp(request):

    if request.method != "POST":
        return redirect("home")

    entered_otp = request.POST.get("otp")

    saved_otp = request.session.get("otp")

    email = request.session.get("otp_email")

    username_form = AuthenticationForm()

    if entered_otp != saved_otp:

        messages.error(request, "Invalid OTP.")

        return render(
            request,
            "index.html",
            {
                "username_form": username_form,
                "show_verify": True,
                "email": email,
            },
        )

    try:

        user = User.objects.get(email=email)

    except User.DoesNotExist():

        messages.error(request, "User not found.")

        return redirect("home")

    login(request, user)

    request.session.pop("otp", None)
    request.session.pop("otp_email", None)

    messages.success(request, "Logged in successfully.")

    return redirect("dashboard")



def verify_register_otp(request):

    if request.method != "POST":
        return redirect("register")

    entered_otp = request.POST.get("otp")

    saved_otp = request.session.get("register_otp")

    data = request.session.get("register_data")

    if not data:

        messages.error(request, "Registration session expired.")

        return redirect("register")

    if entered_otp != saved_otp:

        messages.error(request, "Invalid OTP.")

        return render(
            request,
            "register.html",
            {
                "show_verify": True,
                "email": data["email"],
                "verify_type": "register",
            },
        )

    user = User.objects.create_user(
        username=data["username"],
        first_name=data["first_name"],
        email=data["email"],
        password=data["password"],
    )

    login(request, user)

    request.session.pop("register_otp", None)
    request.session.pop("register_data", None)

    messages.success(
        request,
        "Registration successful!"
    )

    return redirect("dashboard")



@login_required
def profile(request):

    if request.method == "POST":

        form = UpdateProfileForm(
            request.POST,
            instance=request.user
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Name updated successfully."
            )
            return redirect("profile")

    else:

        form = UpdateProfileForm(instance=request.user)

    password_form = SetPasswordForm(request.user)

    return render(
        request,
        "profile.html",
        {
            "form": form,
            "password_form": password_form,
        },
    )


@login_required
def send_password_otp(request):

    otp = random.randint(100000, 999999)

    request.session["password_otp"] = str(otp)

    Thread(
        target=send_otp_email,
        args=(request.user.email, otp),
        daemon=True,
    ).start()

    messages.success(
        request,
        "OTP sent to your registered email."
    )

    return redirect("profile")


@login_required
def verify_password_otp(request):

    if request.method != "POST":
        return redirect("profile")

    if request.POST.get("otp") != request.session.get("password_otp"):

        messages.error(request, "Invalid OTP.")
        return redirect("profile")

    request.session["password_verified"] = True

    messages.success(
        request,
        "OTP verified successfully."
    )

    return redirect("profile")


@login_required
def change_password(request):

    if not request.session.get("password_verified"):

        messages.error(
            request,
            "Please verify OTP first."
        )

        return redirect("profile")

    form = SetPasswordForm(
        request.user,
        request.POST
    )

    if form.is_valid():

        user = form.save()

        update_session_auth_hash(request, user)

        request.session.pop("password_verified", None)
        request.session.pop("password_otp", None)

        messages.success(
            request,
            "Password updated successfully."
        )

    else:

        for error in form.errors.values():
            messages.error(request, error[0])

    return redirect("profile")
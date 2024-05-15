from .forms import ExpenseForm
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import defaultdict
from django.db.models.functions import Coalesce
from django.db.models import Value
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from accounting.models import Expenses, Category
from users.models import CustomUser
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db import transaction
import calendar


def get_month_range(date_str):
    date = datetime.strptime(date_str, "%Y-%m")
    year = date.year
    month = date.month
    _, last_day = calendar.monthrange(year, month)
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month, last_day)
    return [start_date, end_date]


# Create your views here.
class DetailView(LoginRequiredMixin, TemplateView):
    login_url = "/"
    redirect_field_name = "redirect_to"
    template_name = "detail.html"
    context_object_name = "expense_list"
    paginate_by = 20

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["grouped_expenses"] = self.get_grouped_data()

        summary = self.get_summary_data()

        # Format the total spent for each category within each expense type
        total = 0
        for e_type, data in summary.items():
            if e_type == "+":
                total += int(data["total_spent"])
            elif e_type == "-":
                total -= int(data["total_spent"])

            data["total_spent"] = format(int(data["total_spent"]), ",")
            for category_name, total_spent in data["categories"].items():
                data["categories"][category_name] = format(int(total_spent), ",")

        context["summary_data"] = summary
        context["total"] = format(total, ",")

        context["pre_date"] = self.get_previous_month()
        context["next_date"] = self.get_next_month()
        return context

    def get_grouped_data(self):
        raw_data = (
            Expenses.objects.select_related("category")
            .filter(
                username=self.request.user.username,
                e_date__range=get_month_range(self.kwargs["date"]),
            )
            .annotate(
                desc_value=Coalesce("e_desc", Value(""))
            )  # Coalesce to handle NULL values
            .order_by("-e_date")  # 按日期排序
        )
        grouped_expenses = defaultdict(list)
        for expense in raw_data:
            grouped_expenses[expense.e_date].append(expense)

        for date, expenses_in_date in grouped_expenses.items():
            total_amount = sum(
                expense.e_amount if expense.e_type == "+" else -expense.e_amount
                for expense in expenses_in_date
            )
            grouped_expenses[date] = {
                "expenses": expenses_in_date,
                "total_amount": total_amount,
            }
        sorted_grouped_expenses = dict(sorted(grouped_expenses.items(), reverse=True))
        return sorted_grouped_expenses

    def get_summary_data(self):
        # Aggregate expenses for each category and expense type
        category_summary = (
            Expenses.objects.filter(
                username=self.request.user.username,
                e_date__range=get_month_range(self.kwargs["date"]),
            )
            .values("category__c_name", "e_type")
            .annotate(category_total=Sum("e_amount"))
        )

        # Further aggregate category totals for each expense type
        summary_data = {}
        for item in category_summary:
            e_type = item["e_type"]
            category_name = item["category__c_name"]
            category_total = item["category_total"]

            if e_type not in summary_data:
                summary_data[e_type] = {"total_spent": 0, "categories": {}}

            summary_data[e_type]["total_spent"] += category_total

            if category_name not in summary_data[e_type]["categories"]:
                summary_data[e_type]["categories"][category_name] = 0

            summary_data[e_type]["categories"][category_name] += category_total

        return summary_data

    def get_previous_month(self):
        # Convert the current_month string to a datetime object
        current_month_date = timezone.datetime.strptime(self.kwargs["date"], "%Y-%m")

        # Calculate the first day of the current month
        first_day_of_current_month = current_month_date.replace(day=1)

        # Calculate the last day of the previous month
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

        # Extract the year and month of the previous month
        previous_year = last_day_of_previous_month.year
        previous_month = last_day_of_previous_month.month

        # Format the previous year and month as a string
        formatted_previous_month = f"{previous_year}-{previous_month:02d}"

        return formatted_previous_month

    def get_next_month(self):
        # Convert the current_month string to a datetime object
        current_month_date = timezone.datetime.strptime(self.kwargs["date"], "%Y-%m")

        # Calculate the first day of the current month
        first_day_of_current_month = current_month_date.replace(day=1)

        # Calculate the first day of the next month
        if current_month_date.month == 12:  # If current month is December
            first_day_of_next_month = first_day_of_current_month.replace(
                year=current_month_date.year + 1, month=1
            )
        else:
            first_day_of_next_month = first_day_of_current_month.replace(
                month=current_month_date.month + 1
            )

        # Extract the year and month of the next month
        next_year = first_day_of_next_month.year
        next_month = first_day_of_next_month.month

        # Format the next year and month as a string
        formatted_next_month = f"{next_year}-{next_month:02d}"

        return formatted_next_month


@login_required
def saveExpense(request):
    try:
        form = ExpenseForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                if form.cleaned_data["e_id"] == "insert":
                    expense = Expenses(
                        username=CustomUser.objects.get(username=request.user.username),
                        category=Category.objects.get(
                            c_id=form.cleaned_data["category"]
                        ),
                        e_date=form.cleaned_data["date"],
                        e_type=form.cleaned_data["type"],
                        e_amount=form.cleaned_data["amount"],
                        e_desc=form.cleaned_data["desc"],
                    )
                else:
                    expense = Expenses.objects.get(e_id=form.cleaned_data["e_id"])
                    expense.category = Category.objects.get(
                        c_id=form.cleaned_data["category"]
                    )
                    expense.e_date = form.cleaned_data["date"]
                    expense.e_type = form.cleaned_data["type"]
                    expense.e_amount = form.cleaned_data["amount"]
                    expense.e_desc = form.cleaned_data["desc"]
                # Save the user to the database
                expense.save()
                return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})


@login_required
def getEditExpense(request):
    try:
        if request.method == "POST":
            detail = (
                Expenses.objects.values(
                    "category", "e_date", "e_desc", "e_type", "e_amount", "e_id"
                ).filter(username=request.user.username, e_id=request.POST["e_id"])
            ).first()
            return JsonResponse({"success": True, "result": detail})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})


@login_required
def getCategory(request):
    try:
        if request.method == "POST":
            category = Category.objects.values("c_id", "c_type", "c_name").filter(
                username=request.user.username
            )
            return JsonResponse({"success": True, "result": list(category)})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})


@login_required
def delExpense(request):
    try:
        if request.method == "POST":
            with transaction.atomic():
                expense = Expenses.objects.get(
                    e_id=request.POST["e_id"], username=request.user.username
                )
                expense.delete()
            return JsonResponse({"success": True, "result": "刪除成功"})
    except Exception as e:
        return JsonResponse({"success": False, "errors": str(e)})
    return JsonResponse({"success": False})

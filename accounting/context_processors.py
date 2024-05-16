from datetime import datetime


def current_year_month(request):
    current_year_month = datetime.now().strftime("%Y-%m")
    return {"current_year_month": current_year_month}

from django.urls import path
from . import views

from users.views import LoginView, RegistrationView, ConfirmRegistration, InfoView,LoginLineView

app_name = "users"  # app namespace

urlpatterns = [
    path("logout/", views.logout_view, name="logout"),
    path("login/", LoginView.as_view(), name="login"),
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("confirm/", ConfirmRegistration.as_view()),
    path("linktoline/<str:token>/", LoginLineView.as_view(), name="linkToLine"),
    path("cancelLinkToLine/<str:lineId>/", views.cancelLinkToLine, name="cancelLinkToLine"),
    path("info/", InfoView.as_view(), name="info"),
    path("api/chkAcc/", views.chkAcc, name="chkAcc"),
    path("api/saveUser/", views.saveUser, name="saveUser"),
    path("api/delUser/", views.delUser, name="delUser"),
    path("api/changePwd/", views.changePassword, name="changePwd"),
]

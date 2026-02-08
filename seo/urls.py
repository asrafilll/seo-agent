from django.urls import path

from . import views

app_name = "seo"

urlpatterns = [
    path("audit/", views.audit, name="audit"),
    path("audit/<int:pk>/", views.audit_detail, name="audit_detail"),
    path("keywords/", views.keywords, name="keywords"),
    path("optimize/", views.optimize, name="optimize"),
    path("chat/", views.chat, name="chat"),
    path("history/", views.history, name="history"),
]

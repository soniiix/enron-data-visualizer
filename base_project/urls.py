"""
URL configuration for lp2425_projet2_enron project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from base_app import views
from base_app.views.home import home
from base_app.views.people import people
from base_app.views.mails import mails
from base_app.views.statistics import statistics, EmailDetailAPIView, EmailListAPIView
from base_app.views.favorites import favorites

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="accueil"), # PAGE D'ACCUEIL
    path("personnes/", people, name="personnes"),
    path("mails/", mails, name="mails"),
    path("statistiques/", statistics, name="statistiques"),
    path("favoris/", favorites, name="favoris"),
    path('api/emails/', EmailListAPIView.as_view(), name='email-list'),
    path('api/emails/<str:id>/', EmailDetailAPIView.as_view(), name='email-detail'),
]

from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def people(request):
    return render(request, "people.html")

def mails(request):
    return render(request, "mails.html")

def favorites(request):
    return render(request, "favorites.html")
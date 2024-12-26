from django.shortcuts import render

def home(request):
    return render(request, "accueil.html")

def people(request):
    return render(request, "personnes.html")

def mails(request):
    return render(request, "mails.html")

def favorites(request):
    return render(request, "favoris.html")
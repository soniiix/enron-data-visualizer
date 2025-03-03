from django.shortcuts import render

def mails(request):
    return render(request, "mails.html")
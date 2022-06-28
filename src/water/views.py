from django.shortcuts import render

def index(request):
    context = {
    }
    return render(request, "water/index.html", context)

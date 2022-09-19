from django.shortcuts import render


def index(request):
    return render(request, 'compliance/index.html', {'title':'Home'})

from django.shortcuts import render
from .models import User, Account

def index(request):
    # Fetching all records from both models
    users = User.objects.all()
    accounts = Account.objects.all()
    
    return render(request, 'index.html', {
        'users': users,
        'accounts': accounts
    })

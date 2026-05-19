from django.shortcuts import render, redirect
from staff.models import User, Account

def landing_page(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Verify credentials against the Account table
        if Account.objects.filter(email=email, password=password).exists():
            return redirect('temp_dashboard')
        else:
            error = "Authentication failed. Invalid email or password."
            
    return render(request, 'index.html', {'error': error})

def temp_dashboard(request):
    users = User.objects.all()
    accounts = Account.objects.all()
    return render(request, 'admin/dashboard.html', {'users': users, 'accounts': accounts})
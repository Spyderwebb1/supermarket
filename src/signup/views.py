from django.http import HttpResponseRedirect
from django.shortcuts import render
from signup.forms import SignUpForm
from django.contrib.auth import login
from django.urls import reverse 
# Create your views here.


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            user = form.save()
            print(user.email)
            login(request, user)
            return HttpResponseRedirect(reverse('catalog:home'))
    
    else:
        form = SignUpForm()
    print(form)
    return render(request, 'signup/signup.html', {
        'form': form,
    })
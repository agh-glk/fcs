from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import forms
from fcs.manager.models import User


def registration_complete(request):
    return render(request, 'registration_complete.html')


@login_required()
def password_change_complete(request):
    messages.success(request, "Password changed!")
    return redirect('index')


def account_disabled(request, username):
    messages.error(request, "Your account is disabled! It must be activated by mail.")
    return redirect('index')


@login_required()
def edit_user_data(request, username):
    user = get_object_or_404(User, id=request.user.id)
    form = forms.EditUserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, "Your data updated!")
        return redirect('index')
    return render(request, 'edit_user_data.html', {'form': form})

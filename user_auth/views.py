from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm


@login_required
def profile(request):
    if request.method == 'POST':
         user_form = UserUpdateForm(request.POST, instance=request.user)

         if user_form.is_valid():
            user_form.save()
            messages.success(request, f"Your account has been updated!")
            return redirect('profile')
    else:
         user_form = UserUpdateForm(request.POST, instance=request.user)


    context = {
        'u_form': user_form
    }
    return render(request, 'user_auth/profile.html', context)

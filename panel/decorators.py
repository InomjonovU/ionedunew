from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def staff_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')
        if not request.user.is_staff:
            messages.error(request, 'Bu sahifaga kirish uchun admin huquqlari kerak.')
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapped

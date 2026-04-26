from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .models import Notification


@login_required
def notification_list_view(request):
    notifications = (
        Notification.objects
        .filter(user=request.user)
        .order_by('-created_at')
    )
    # Ko'rilgan deb belgilash
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def unread_count_ajax(request):
    """AJAX: o'qilmagan bildirishnomalar soni (navbar uchun)."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def mark_all_read_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})

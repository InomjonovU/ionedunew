from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Certificate


@login_required
def certificate_list_view(request):
    certificates = (
        Certificate.objects
        .filter(user=request.user)
        .select_related('quiz')
        .order_by('-issued_at')
    )
    return render(request, 'certificates/list.html', {'certificates': certificates})


def certificate_detail_view(request, uuid):
    """Ochiq URL — login talab qilinmaydi (tekshirish uchun)."""
    certificate = get_object_or_404(Certificate, uuid=uuid)
    context = {'certificate': certificate, 'is_owner': request.user == certificate.user}
    return render(request, 'certificates/detail.html', context)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from . import views
from . import admin as _admin_customization  # noqa: F401 — admin site sozlamalari

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
    path('faq/', TemplateView.as_view(template_name='pages/faq.html'), name='faq'),
    path('', include('accounts.urls')),
    path('subjects/', include('subjects.urls')),
    path('lessons/', include('lessons.urls')),
    path('tests/', include('quizzes.urls')),
    path('library/', include('library.urls')),
    path('certificates/', include('certificates.urls')),
    path('notifications/', include('notifications.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('panel/', include('panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

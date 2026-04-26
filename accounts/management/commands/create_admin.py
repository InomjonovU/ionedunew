from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = "Admin foydalanuvchi yaratish yoki mavjudini staff/superuser qilish"

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Foydalanuvchi nomi')
        parser.add_argument('--password', default='admin123', help='Parol')
        parser.add_argument('--email', default='admin@edusphere.uz', help='Email')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Admin',
                'last_name': 'EduSphere',
            }
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"OK Admin yaratildi: username='{username}', password='{password}'"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"OK Mavjud foydalanuvchi admin qilindi: username='{username}', password='{password}'"
            ))
        self.stdout.write(f"   Panel: http://127.0.0.1:8000/panel/")
        self.stdout.write(f"   Django Admin: http://127.0.0.1:8000/admin/")

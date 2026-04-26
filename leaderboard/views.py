from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

User = get_user_model()


@login_required
def leaderboard_view(request):
    # Umumiy reyting — top 50
    global_top = (
        User.objects
        .filter(is_active=True, is_staff=False)
        .order_by('-total_score')[:50]
    )

    # Sinf ichida reyting (faqat login qilgan foydalanuvchining sinfi)
    class_top = []
    user_grade = request.user.grade
    if user_grade:
        class_top = (
            User.objects
            .filter(is_active=True, is_staff=False, grade=user_grade)
            .order_by('-total_score')[:50]
        )

    # Joriy foydalanuvchining o'rni
    global_rank = (
        User.objects
        .filter(is_active=True, is_staff=False, total_score__gt=request.user.total_score)
        .count() + 1
    )
    class_rank = None
    if user_grade:
        class_rank = (
            User.objects
            .filter(
                is_active=True, is_staff=False,
                grade=user_grade,
                total_score__gt=request.user.total_score
            )
            .count() + 1
        )

    context = {
        'global_top': global_top,
        'class_top': class_top,
        'global_rank': global_rank,
        'class_rank': class_rank,
        'user_grade': user_grade,
    }
    return render(request, 'leaderboard/leaderboard.html', context)

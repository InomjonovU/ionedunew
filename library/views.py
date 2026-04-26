from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render

from subjects.models import Subject

from .forms import LibrarySearchForm
from .models import LibraryItem, LibraryItemView


@login_required
def library_list_view(request):
    form = LibrarySearchForm(request.GET or None)
    items = LibraryItem.objects.filter(is_published=True).select_related('subject')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        subject_id = form.cleaned_data.get('subject')
        grade = form.cleaned_data.get('grade')
        item_type = form.cleaned_data.get('item_type')

        if q:
            items = items.filter(title__icontains=q)
        if subject_id:
            items = items.filter(subject_id=subject_id)
        if grade:
            items = items.filter(grade=grade)
        if item_type:
            items = items.filter(item_type=item_type)

    subjects = Subject.objects.filter(is_active=True)
    context = {
        'items': items.order_by('-created_at'),
        'form': form,
        'subjects': subjects,
    }
    return render(request, 'library/list.html', context)


@login_required
def library_item_view(request, pk):
    item = get_object_or_404(LibraryItem, pk=pk, is_published=True)

    view_obj, created = LibraryItemView.objects.get_or_create(
        user=request.user, item=item
    )
    if created:
        LibraryItem.objects.filter(pk=item.pk).update(
            view_count=item.view_count + 1
        )

    context = {'item': item}
    return render(request, 'library/detail.html', context)


@login_required
def library_download_view(request, pk):
    item = get_object_or_404(LibraryItem, pk=pk, is_published=True)

    if not item.file:
        raise Http404

    LibraryItem.objects.filter(pk=item.pk).update(
        download_count=item.download_count + 1
    )
    LibraryItemView.objects.filter(
        user=request.user, item=item
    ).update(downloaded=True)

    response = FileResponse(item.file.open('rb'), as_attachment=True)
    response['Content-Disposition'] = f'attachment; filename="{item.file.name.split("/")[-1]}"'
    return response

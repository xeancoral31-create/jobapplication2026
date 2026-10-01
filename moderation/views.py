"""moderation/views.py - Stub views for Stage 0."""
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Flag


@staff_member_required
def flag_list(request):
    flags = Flag.objects.select_related("reporter", "content_type")
    return render(request, "moderation/flag_list.html", {"flags": flags})


@staff_member_required
def flag_detail(request, pk):
    flag = get_object_or_404(Flag, pk=pk)
    return render(request, "moderation/flag_detail.html", {"flag": flag})


@login_required
def report_content(request, content_type, object_id):
    return render(
        request,
        "moderation/report.html",
        {"content_type": content_type, "object_id": object_id},
    )

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import selectors

@login_required
def activity_feed_view(request):
    activities = selectors.get_user_activity_feed(request.user)
    return render(request, 'audit/activity_feed.html', {'activities': activities})
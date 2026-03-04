from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import services
from groups.selectors import get_user_groups

@login_required
def dashboard_view(request):
    summary = services.get_dashboard_summary(request.user)

    recent_groups = get_user_groups(request.user)[:3]
    
    context = {
        'summary': summary,
        'recent_groups': recent_groups
    }
    return render(request, 'ledger/dashboard.html', context)
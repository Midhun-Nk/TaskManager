from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    """
    decorator for views: allowed_roles can be tuple/list of role strings.
    Example usage: @role_required(['SUPERADMIN'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')  # or HttpResponseForbidden()
            if user.role not in allowed_roles:
                return HttpResponseForbidden("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

is_superadmin = role_required(['SUPERADMIN'])
is_admin = role_required(['ADMIN'])
is_superadmin_or_admin = role_required(['SUPERADMIN','ADMIN'])

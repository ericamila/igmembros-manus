from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.core.exceptions import PermissionDenied

def admin_required(function):
    """
    Decorator para views que verifica se o usuário é administrador.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'admin':
            return function(request, *args, **kwargs)
        raise PermissionDenied
    return wrap

def role_required(roles):
    """
    Decorator para views que verifica se o usuário tem uma das funções especificadas.
    Uso: @role_required(['admin', 'pastor'])
    """
    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in roles:
                return function(request, *args, **kwargs)
            raise PermissionDenied
        return wrap
    return decorator

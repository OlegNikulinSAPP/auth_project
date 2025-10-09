# auth_system/permissions.py
from django.http import JsonResponse
from .models import AccessRule, UserRole, BusinessElement


def check_permission(user, element_name, action):
    """
    Проверяет, есть ли у пользователя право на действие с элементом
    """
    try:
        element = BusinessElement.objects.get(name=element_name)
    except BusinessElement.DoesNotExist:
        return False

    # Получаем все роли пользователя
    user_roles = UserRole.objects.filter(user=user).values_list('role', flat=True)

    # Ищем подходящее правило доступа
    access_rule = AccessRule.objects.filter(
        role__in=user_roles,
        element=element
    ).first()

    if not access_rule:
        return False

    # Сопоставляем действие с полем в модели
    permission_map = {
        'read': access_rule.read_permission,
        'create': access_rule.create_permission,
        'update': access_rule.update_permission,
        'delete': access_rule.delete_permission,
        'read_all': access_rule.read_all_permission,
        'update_all': access_rule.update_all_permission,
        'delete_all': access_rule.delete_all_permission,
    }

    return permission_map.get(action, False)


def permission_required(element_name, action):
    """
    Декоратор для проверки прав доступа к view
    """

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user'):
                return JsonResponse({'error': 'Authentication required'}, status=401)

            if check_permission(request.user, element_name, action):
                return view_func(request, *args, **kwargs)
            else:
                return JsonResponse({'error': 'Forbidden'}, status=403)

        return wrapper

    return decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from datetime import datetime, timedelta

from .models import User, Session, UserRole, Role
from .permissions import permission_required
from django.utils import timezone

import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        logging.info(f"[class RegisterView] Обрабатываю запрос: {request.path}")
        try:
            data = json.loads(request.body)

            logging.info(f"[class RegisterView] Получены данные: {data}")

            # Проверяем обязательные поля
            required_fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm']
            for field in required_fields:
                if field not in data:
                    logging.error(f"[class RegisterView] Отсутствующее поле: {field}")
                    return JsonResponse({'error': f'Отсутствующее поле: {field}'}, status=400)

            # Проверяем совпадение паролей
            if data['password'] != data['password_confirm']:
                logging.error("[class RegisterView] Пароли не совпадают")
                return JsonResponse({'error': 'Пароли не совпадают'}, status=400)

            # Проверяем уникальность email
            if User.objects.filter(email=data['email']).exists():
                logging.error("[class RegisterView] Пользователь с таким адресом электронной почты уже существует")
                return JsonResponse({'error': 'Пользователь с таким адресом электронной почты уже существует'},
                                    status=400)

            # Создаем пользователя
            user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                patronymic=data.get('patronymic', ''),
                email=data['email']
            )
            user.set_password(data['password'])
            user.save()

            logging.info(f"[class RegisterView] Пользователь успешно создан, user_id: {user.pk}")

            # Назначаем базовую роль (например, "user")
            try:
                user_role = Role.objects.get(name='user')
                UserRole.objects.create(user=user, role=user_role)
                logging.info(f"[class RegisterView] Пользователю с user_id: {user.pk} назначена роль: 'user'")
            except Role.DoesNotExist:
                logging.error("[class RegisterView] Ошибка при назначении роли пользователю")

            return JsonResponse({
                'message': 'Пользователь успешно зарегистрировался',
                'user_id': user.pk
            }, status=201)

        except json.JSONDecodeError:
            logging.error("[class RegisterView] Invalid json")
            return JsonResponse({'error': 'Invalid json'}, status=400)
        except Exception as e:
            logging.error(f"[class RegisterView] Ошибка при регистрации пользователя: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        logging.info(f"[class LoginView] Обрабатываю запрос: {request.path}")
        try:
            data = json.loads(request.body)

            logging.info(f"[class LoginView] Получены данные: {data}")

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                logging.error("[class LoginView] Требуются адрес электронной почты и пароль")
                return JsonResponse({'error': 'Требуются адрес электронной почты и пароль'}, status=400)

            try:
                user = User.objects.get(email=email, is_active=True)
                logging.info("[class LoginView] Пользователь найден в БД")
            except User.DoesNotExist:
                logging.error("[class LoginView] Неверные учетные данные")
                return JsonResponse({'error': 'Неверные учетные данные'}, status=401)

            if user.check_password(password):
                logging.info("[class LoginView] Пароль проверен")
                # Генерируем токен
                token = user.generate_token()
                logging.info("[class LoginView] Токен сгенерирован")

                # Создаем сессию
                expires_at = timezone.now() + timedelta(days=1)
                logging.info(f"[class LoginView] Сессия создана, время действия {expires_at}")
                Session.objects.create(
                    user=user,
                    token=token,
                    expires_at=expires_at
                )

                return JsonResponse({
                    'token': token,
                    'user_id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                })
            else:
                logging.error("[class LoginView] Неверный пароль")
                return JsonResponse({'error': 'Неверный пароль'}, status=401)

        except json.JSONDecodeError:
            logging.error("[class LoginView] Invalid JSON")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        logging.info(f"[class LogoutView] Обрабатываю запрос: {request.path}")
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logging.info(f"[class LogoutView] HTTP_AUTHORIZATION: {auth_header}")

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            Session.objects.filter(token=token).delete()

        logging.info("[class LogoutView] Пользователь успешно вышел из системы")
        return JsonResponse({'message': 'Logged out successfully'})


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(View):
    def get(self, request):
        logging.info(f"[ProfileView] Обрабатываю запрос: {request.path}")
        if not hasattr(request, 'user'):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        user = request.user
        return JsonResponse({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'patronymic': user.patronymic,
            'email': user.email,
            'is_active': user.is_active
        })

    def put(self, request):
        if not hasattr(request, 'user'):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            data = json.loads(request.body)
            user = request.user

            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'patronymic' in data:
                user.patronymic = data['patronymic']

            user.save()

            return JsonResponse({'message': 'Profile updated successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteAccountView(View):
    def delete(self, request):
        if not hasattr(request, 'user'):
            return JsonResponse({'error': 'Authentication required'}, status=401)

        user = request.user
        user.is_active = False
        user.save()

        # Удаляем все сессии пользователя
        Session.objects.filter(user=user).delete()

        return JsonResponse({'message': 'Account deleted successfully'})


# Mock бизнес-объекты для демонстрации
@method_decorator(csrf_exempt, name='dispatch')
class ProductsView(View):
    @method_decorator(permission_required('products', 'read'))
    def get(self, request):
        # Mock данные о продуктах
        products = [
            {'id': 1, 'name': 'Laptop', 'price': 1000},
            {'id': 2, 'name': 'Phone', 'price': 500},
            {'id': 3, 'name': 'Tablet', 'price': 300},
        ]
        return JsonResponse({'products': products})

    @method_decorator(permission_required('products', 'create'))
    def post(self, request):
        return JsonResponse({'message': 'Product created'})


@method_decorator(csrf_exempt, name='dispatch')
class OrdersView(View):
    @method_decorator(permission_required('orders', 'read'))
    def get(self, request):
        # Mock данные о заказах
        orders = [
            {'id': 1, 'product': 'Laptop', 'status': 'completed'},
            {'id': 2, 'product': 'Phone', 'status': 'pending'},
        ]
        return JsonResponse({'orders': orders})


@method_decorator(csrf_exempt, name='dispatch')
class AssignRoleView(View):
    @method_decorator(permission_required('users', 'update_all'))
    def post(self, request):
        data = json.loads(request.body)
        user_id = data['user_id']
        role_name = data['role_name']

        user = User.objects.get(id=user_id)
        role = Role.objects.get(name=role_name)

        # Удаляем старые роли (опционально)
        UserRole.objects.filter(user=user).delete()

        # Назначаем новую роль
        UserRole.objects.create(user=user, role=role)

        return JsonResponse({'message': f'Роль {role_name} назначена пользователю {user.email}'})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from datetime import datetime, timedelta

from .models import User, Session, UserRole, Role
from .permissions import permission_required


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        # Выводим информацию о запросе в консоль
        print("=== REGISTER REQUEST ===")
        print(f"Method: {request.method}")
        print(f"Path: {request.path}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {request.body}")
        print(f"Content-Type: {request.content_type}")
        print("========================")

        try:
            data = json.loads(request.body)

            # Проверяем обязательные поля
            required_fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)

            # Проверяем совпадение паролей
            if data['password'] != data['password_confirm']:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            # Проверяем уникальность email
            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'error': 'User with this email already exists'}, status=400)

            # Создаем пользователя
            user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                patronymic=data.get('patronymic', ''),
                email=data['email']
            )
            user.set_password(data['password'])
            user.save()

            # Назначаем базовую роль (например, "user")
            try:
                user_role = Role.objects.get(name='user')
                UserRole.objects.create(user=user, role=user_role)
            except Role.DoesNotExist:
                pass

            return JsonResponse({
                'message': 'User registered successfully',
                'user_id': user.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password required'}, status=400)

            try:
                user = User.objects.get(email=email, is_active=True)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

            if user.check_password(password):
                # Генерируем токен
                token = user.generate_token()

                # Создаем сессию
                expires_at = datetime.now() + timedelta(days=1)
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
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            Session.objects.filter(token=token).delete()

        return JsonResponse({'message': 'Logged out successfully'})


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(View):
    def get(self, request):
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

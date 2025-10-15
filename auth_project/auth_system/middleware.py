from django.http import JsonResponse
import jwt
from django.conf import settings
from .models import User, Session

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        logging.info('[class JWTAuthenticationMiddleware] Middleware ЗАПУЩЕН!')
        self.get_response = get_response

    def __call__(self, request):
        logging.info(f"[class JWTAuthenticationMiddleware] Обрабатываю запрос: {request.path}")
        # Пропускаем публичные эндпоинты
        public_paths = ['/api/register/', '/api/login/']
        if any(request.path.startswith(path) for path in public_paths):
            logging.info('[class JWTAuthenticationMiddleware] Пропускаю публичные эндпоинты и передаю следующему '
                         'middleware')
            return self.get_response(request)

        # Получаем токен из заголовка Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logging.info(f"[class JWTAuthenticationMiddleware] HTTP_AUTHORIZATION: {auth_header}")

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]

            try:
                # Декодируем JWT токен
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')

                # Проверяем существование пользователя и активность сессии
                try:
                    user = User.objects.get(id=user_id, is_active=True)
                    session = Session.objects.filter(user=user, token=token).first()

                    if session and not session.is_expired():
                        request.user = user
                    else:
                        return JsonResponse({'error': 'Session expired'}, status=401)

                except User.DoesNotExist:
                    logging.error(f"User {user_id} not found or inactive")
                    return JsonResponse({'error': 'User not found'}, status=401)

            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        return self.get_response(request)

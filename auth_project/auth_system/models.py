from django.db import models
import bcrypt
import jwt
from datetime import datetime, timedelta, UTC
from django.conf import settings


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, password):
        """Хеширование пароля с помощью bcrypt"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Проверка пароля"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def generate_token(self):
        """Генерация JWT токена"""
        payload = {
            'user_id': self.pk,
            'exp': datetime.now(UTC) + timedelta(days=1),
            'iat': datetime.now(UTC)
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Бизнес-сущности, к которым нужен доступ"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AccessRule(models.Model):
    """Правила доступа ролей к бизнес-сущностям"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE)

    # Базовые права
    read_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)

    # Права на все объекты (не только свои)
    read_all_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ['role', 'element']


class UserRole(models.Model):
    """Связь пользователя с ролью"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'role']


class Session(models.Model):
    """Активные сессии пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return datetime.now() > self.expires_at
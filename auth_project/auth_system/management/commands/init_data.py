from django.core.management.base import BaseCommand
from django.apps import apps

Role = apps.get_model('auth_system', 'Role')
BusinessElement = apps.get_model('auth_system', 'BusinessElement')
AccessRule = apps.get_model('auth_system', 'AccessRule')


class Command(BaseCommand):
    help = 'Initialize basic roles and permissions'

    def handle(self, *args, **options):
        # Создаем роли
        roles = [
            {'name': 'admin', 'description': 'Administrator with full access'},
            {'name': 'user', 'description': 'Regular user'},
            {'name': 'manager', 'description': 'Manager with extended permissions'},
        ]

        for role_data in roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(f'Created role: {role.name}')

        # Создаем бизнес-элементы
        elements = [
            {'name': 'products', 'description': 'Product management'},
            {'name': 'orders', 'description': 'Order management'},
            {'name': 'users', 'description': 'User management'},
        ]

        for element_data in elements:
            element, created = BusinessElement.objects.get_or_create(
                name=element_data['name'],
                defaults={'description': element_data['description']}
            )
            if created:
                self.stdout.write(f'Created element: {element.name}')

        # Создаем правила доступа
        admin_role = Role.objects.get(name='admin')
        for element in BusinessElement.objects.all():
            AccessRule.objects.get_or_create(
                role=admin_role,
                element=element,
                defaults={
                    'read_permission': True,
                    'read_all_permission': True,
                    'create_permission': True,
                    'update_permission': True,
                    'update_all_permission': True,
                    'delete_permission': True,
                    'delete_all_permission': True,
                }
            )

        user_role = Role.objects.get(name='user')
        user_elements = BusinessElement.objects.filter(name__in=['products', 'orders'])

        for element in user_elements:
            AccessRule.objects.get_or_create(
                role=user_role,
                element=element,
                defaults={
                    'read_permission': True,  # Может читать свои
                    'create_permission': True,  # Может создавать
                    'update_permission': True,  # Может изменять свои
                    'delete_permission': True,  # Может удалять свои
                    # _all_permission = False (по умолчанию)
                }
            )

        manager_role = Role.objects.get(name='manager')
        for element in BusinessElement.objects.all():
            AccessRule.objects.get_or_create(
                role=manager_role,
                element=element,
                defaults={
                    'read_permission': True,
                    'read_all_permission': True,  # Может читать ВСЕ
                    'create_permission': True,
                    'update_permission': True,
                    'update_all_permission': True,  # Может изменять ВСЕ
                    'delete_permission': True,
                    # delete_all_permission = False (не может удалять все)
                }
            )

        self.stdout.write('Initial data created successfully!')
from django.core.management.base import BaseCommand
from auth_system.models import Role, BusinessElement, AccessRule


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

        # Создаем правила доступа для админа
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

        self.stdout.write('Initial data created successfully!')
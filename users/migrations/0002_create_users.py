from django.db import migrations

def inserir_usuario(apps):
    User = apps.get_model('users', 'CustomUser')

    tesoureiro = User.objects.create_user(
        username='tesoureiro@email.com',
        email='tesoureiro@email.com',
        password='confirmar',
        role='tesoureiro',
        is_active=True,
        is_staff=False,
        first_name='Tesoureiro',
        last_name='Teste',
        phone='(00) 00000-5555',
        address='Endereço de teste'
    )
    tesoureiro.save()

    secretario = User.objects.create_user(
        username='secretario@email.com',
        email='secretario@email.com',
        password='confirmar',
        role='secretario',
        is_active=True,
        is_staff=False,
        first_name='Secretario',
        last_name='Teste',
        phone='(00) 00000-4444',
        address='Endereço de teste'
    )
    secretario.save()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(inserir_usuario),
    ]
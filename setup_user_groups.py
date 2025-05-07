# Script para configurar grupos e permissões de usuários
import os
import django

def setup_groups_and_permissions():
    # Configura o ambiente Django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "templo_digital_django.settings")
    django.setup()

    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType

    # Definição dos modelos por app (simplificado, ajuste conforme seus modelos exatos)
    APP_MODELS = {
        "members": ["member"],
        "churches": ["church"],
        "school": ["schoolclass", "student", "attendancerecord"],
        "events": ["event", "eventsubscription"],
        "finances": ["category", "transaction"],
        "core": ["churchconfiguration"],
        "auth": ["user"] # Para gerenciar usuários
    }

    # Permissões CRUD padrão
    CRUD_PERMISSIONS = ["add", "change", "delete", "view"]

    # Definição dos perfis e suas permissões
    # Estrutura: "NomeDoGrupo": { "app_label": { "model_name": ["perm1", "perm2"] } }
    # Se for CRUD completo para um modelo, pode usar "all_crud"
    # Se for apenas leitura, ["view"]
    PROFILES = {
        "Admin": {
            "members": {"member": "all_crud"},
            "churches": {"church": "all_crud"},
            "school": {
                "schoolclass": "all_crud", 
                "student": "all_crud", 
                "attendancerecord": "all_crud"
            },
            "events": {
                "event": "all_crud", 
                "eventsubscription": "all_crud"
            },
            "finances": {
                "category": "all_crud", 
                "transaction": "all_crud"
            },
            "core": {"churchconfiguration": "all_crud"},
            "auth": {"user": "all_crud"} # Admin pode gerenciar usuários
        },
        "Secretário": {
            "members": {"member": "all_crud"},
            "churches": {"church": "all_crud"},
            "school": {
                "schoolclass": "all_crud", 
                "student": "all_crud", 
                "attendancerecord": "all_crud"
            },
            "events": {
                "event": "all_crud", 
                "eventsubscription": "all_crud"
            },
            "finances": {
                "category": ["view"], 
                "transaction": ["view"]
            },
            "core": {"churchconfiguration": ["view"]}
        },
        "Tesoureiro": {
            "finances": {
                "category": "all_crud", 
                "transaction": "all_crud"
            },
            "members": {"member": ["view"]},
            "churches": {"church": ["view"]},
            "school": {
                "schoolclass": ["view"], 
                "student": ["view"], 
                "attendancerecord": ["view"]
            },
            "events": {
                "event": ["view"], 
                "eventsubscription": ["view"]
            },
            "core": {"churchconfiguration": ["view"]}
        }
    }

    for group_name, app_perms in PROFILES.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"Grupo \'{group_name}\' criado.")
        else:
            print(f"Grupo \'{group_name}\' já existe. Limpando permissões antigas...")
            group.permissions.clear()

        for app_label, model_perms in app_perms.items():
            for model_name, permissions_needed in model_perms.items():
                try:
                    content_type = ContentType.objects.get(app_label=app_label, model=model_name.lower())
                    model_class_permissions = []
                    if permissions_needed == "all_crud":
                        perms_to_assign = CRUD_PERMISSIONS
                    else:
                        perms_to_assign = permissions_needed
                    
                    for perm_codename_suffix in perms_to_assign:
                        codename = f"{perm_codename_suffix}_{model_name.lower()}"
                        try:
                            perm = Permission.objects.get(content_type=content_type, codename=codename)
                            model_class_permissions.append(perm)
                        except Permission.DoesNotExist:
                            print(f"AVISO: Permissão \'{codename}\' não encontrada para {app_label}.{model_name}")

                    if model_class_permissions:
                        group.permissions.add(*model_class_permissions)
                        print(f"  Permissões para {app_label}.{model_name} ({[p.codename for p in model_class_permissions]}) adicionadas ao grupo \'{group_name}\'")
                except ContentType.DoesNotExist:
                    print(f"ERRO: ContentType para {app_label}.{model_name} não encontrado. Verifique os nomes do app e modelo.")
        print(f"Permissões para o grupo \'{group_name}\' configuradas.")

if __name__ == "__main__":
    print("Iniciando configuração de grupos e permissões...")
    setup_groups_and_permissions()
    print("Configuração de grupos e permissões concluída.")



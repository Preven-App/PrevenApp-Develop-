from app_prevenapp.models import Usuario, Profesional

def callback(request, context):
    try:
        usuarios_count = Usuario.objects.count()
        profesionales_count = Profesional.objects.count()
    except Exception as e:
        # Si hay un error con la BD, se imprimirá en consola y mostrará 0
        print(f"Error en el dashboard: {e}")
        usuarios_count = 0
        profesionales_count = 0

    context.update({
        "kpi": {
            "total_usuarios": usuarios_count,
            "total_profesionales": profesionales_count,
        }
    })
    return context
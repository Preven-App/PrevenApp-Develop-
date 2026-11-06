from django.shortcuts import render
import google.generativeai as genai

def landing_page(request):
    return render(request, 'app_prevenapp/landing.html')

def login_view(request):
    return render(request, 'app_prevenapp/login.html')

def register_view(request):
    return render(request, 'app_prevenapp/register.html')

# --- MÓDULO DE COMUNICACIÓN ---

API_KEY = "TU_API_KEY_AQUI"  # Mantén tu clave real que empieza por AIzaSy...
genai.configure(api_key=API_KEY)

# Lista de identificadores de modelos activos en la API
MODELOS_DISPONIBLES = [
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
]

def chatbot_view(request):
    bot_msg = ""
    user_msg = None

    if request.method == 'POST':
        user_msg = request.POST.get('mensaje', '')
        
        prompt = (
            "Eres el asistente virtual empático y profesional de una aplicación "
            "para adolescentes llamada PrevenApp. Responde esta duda sobre educación sexual, "
            "métodos anticonceptivos o prevención del embarazo de forma clara, directa y respetuosa "
            f"(máximo 3 párrafos cortos): {user_msg}"
        )
        
        # Intenta consultar los modelos disponibles en secuencia
        exito = False
        for nombre_modelo in MODELOS_DISPONIBLES:
            try:
                model = genai.GenerativeModel(nombre_modelo)
                respuesta = model.generate_content(prompt)
                bot_msg = respuesta.text
                exito = True
                break
            except Exception as e:
                print(f"[DEBUG] Falló el modelo {nombre_modelo}: {e}")
                continue

        if not exito:
            bot_msg = "Lo siento, la IA no se encuentra disponible momentáneamente. Revisa la validez de tu API Key."

    return render(request, 'app_prevenapp/chatbot.html', {
        'user_msg': user_msg,
        'bot_msg': bot_msg
    })

def chat_personal_view(request):
    return render(request, 'app_prevenapp/chat_personal.html')

def salas_chat_view(request):
    return render(request, 'app_prevenapp/salas_chat.html')
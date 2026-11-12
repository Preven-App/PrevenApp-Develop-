import os
from django.shortcuts import render
from django.http import JsonResponse
import json
from groq import Groq

def landing_page(request):
    return render(request, 'app_prevenapp/landing.html')

def login_view(request):
    return render(request, 'app_prevenapp/login.html')

def register_view(request):
    return render(request, 'app_prevenapp/register.html')

def chat_personal_view(request):
    return render(request, 'app_prevenapp/chat_personal.html')

def salas_chat_view(request):
    return render(request, 'app_prevenapp/salas_chat.html')

# --- MÓDULO DE INTELIGENCIA ARTIFICIAL (GROQ API) ---
# Se lee de forma segura desde el sistema para proteger tu clave en GitHub
client = Groq(api_key="") #COLOCAR TU CLAVE DE API AQUÍ ary 

def chatbot_view(request):
    """
    Vista del chat de PrevenApp optimizada para texto libre mediante AJAX.
    """
    bot_msg = "¡Hola! Soy el asistente virtual de PrevenApp. ¿Qué duda tienes sobre salud sexual o prevención?"

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('mensaje', '').strip()

            if not user_message:
                return JsonResponse({'respuesta': 'Por favor, escribe una pregunta válida.'}, status=400)

            # Consulta a la IA de Groq
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres el asistente virtual oficial de PrevenApp, una aplicación dirigida a adolescentes. "
                            "Tu tarea es brindar educación y respuestas claras, empáticas y breves sobre "
                            "salud sexual, métodos anticonceptivos y prevención de embarazo. "
                            "Responde en un tono amigable, en máximo 2 párrafos y siempre con rigor médico preventivo."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
                model="openai/gpt-oss-120b",
                max_completion_tokens=2048,
                reasoning_effort="medium",
            )

            respuesta = chat_completion.choices[0].message.content
            return JsonResponse({'respuesta': respuesta})

        except Exception as e:
            return JsonResponse({'respuesta': f'Lo siento, ocurrió un problema al conectar con la IA: {str(e)}'}, status=500)

    return render(request, 'app_prevenapp/chatbot.html', {
        'bot_msg': bot_msg
    })
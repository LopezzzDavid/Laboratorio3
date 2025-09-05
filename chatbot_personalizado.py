import requests
import json
import datetime
import os

# Configuración del chatbot
class ChatbotConfig:
    def __init__(self):
        self.API_KEY = 'sk-53751d5c6f344a5dbc0571de9f51313e'
        self.API_URL = 'https://api.deepseek.com/v1/chat/completions'
        self.modelo = 'deepseek-chat'
        
        # PERSONALIZACIÓN: Define la personalidad de tu chatbot
        self.personalidad = {
            "nombre": "Asistente Personal",
            "rol": "un asistente útil y amigable",
            "tono": "profesional pero cercano",
            "especialidad": "ayudar con preguntas generales y tareas cotidianas",
            "idioma": "español",
            # Puedes cambiar estos valores según lo que necesites
        }
        
        # Sistema de prompt personalizable
        self.sistema_prompt = f"""
        Eres {self.personalidad['nombre']}, {self.personalidad['rol']}.
        Tu tono de comunicación es {self.personalidad['tono']}.
        Te especializas en {self.personalidad['especialidad']}.
        Siempre respondes en {self.personalidad['idioma']}.
        
        Comportamientos específicos:
        - Sé conciso pero completo en tus respuestas
        - Si no sabes algo, admítelo honestamente
        - Ofrece ejemplos cuando sea útil
        - Mantén un tono amigable y profesional
        
        Responde de manera natural y conversacional.
        """

class ChatbotPersonalizado:
    def __init__(self):
        self.config = ChatbotConfig()
        self.historial_conversacion = []
        self.max_historial = 10  # Mantiene las últimas 10 interacciones
        
    def agregar_al_historial(self, rol, contenido):
        """Mantiene un historial de conversación para contexto"""
        self.historial_conversacion.append({"role": rol, "content": contenido})
        
        # Limitar el tamaño del historial
        if len(self.historial_conversacion) > self.max_historial * 2:  # *2 porque hay usuario y asistente
            self.historial_conversacion = self.historial_conversacion[-self.max_historial * 2:]
    
    def preparar_mensajes(self, mensaje_usuario):
        """Prepara los mensajes incluyendo el sistema prompt y el historial"""
        mensajes = [{"role": "system", "content": self.config.sistema_prompt}]
        
        # Agregar historial de conversación
        mensajes.extend(self.historial_conversacion)
        
        # Agregar mensaje actual del usuario
        mensajes.append({"role": "user", "content": mensaje_usuario})
        
        return mensajes
    
    def enviar_mensaje(self, mensaje_usuario):
        """Envía mensaje a la API con personalización y contexto"""
        headers = {
            'Authorization': f'Bearer {self.config.API_KEY}',
            'Content-Type': 'application/json'
        }
        
        mensajes = self.preparar_mensajes(mensaje_usuario)
        
        data = {
            'model': self.config.modelo,
            'messages': mensajes,
            'temperature': 0.7,  # Controla la creatividad (0.0 - 1.0)
            'max_tokens': 1000,  # Límite de tokens en la respuesta
        }
        
        try:
            print("Enviando solicitud a la API...")
            response = requests.post(self.config.API_URL, headers=headers, json=data, timeout=30)
            
            print(f"Código de respuesta: {response.status_code}")
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                respuesta = response_data['choices'][0]['message']['content']
                
                # Agregar al historial
                self.agregar_al_historial("user", mensaje_usuario)
                self.agregar_al_historial("assistant", respuesta)
                
                return respuesta
            else:
                return f"Respuesta inesperada de la API: {response_data}"
                
        except requests.exceptions.ConnectionError:
            return "❌ Error: No se puede conectar a la API. Verifica tu conexión a internet."
        except requests.exceptions.Timeout:
            return "⏰ Error: La solicitud tardó demasiado tiempo. Inténtalo de nuevo."
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                return "🔑 Error: API Key inválida o expirada."
            elif err.response.status_code == 429:
                return "📊 Error: Has excedido el límite de solicitudes. Espera un momento."
            else:
                try:
                    error_detail = err.response.json()
                    return f"❌ Error de la API ({err.response.status_code}): {error_detail}"
                except:
                    return f"❌ Error de la API ({err.response.status_code}): {err.response.text}"
        except json.JSONDecodeError:
            return "❌ Error: La respuesta de la API no es válida."
        except Exception as e:
            return f"❌ Error inesperado: {e}"
    
    def mostrar_info_chatbot(self):
        """Muestra información sobre la personalización del chatbot"""
        print(f"\n🤖 Información del Chatbot:")
        print(f"   • Nombre: {self.config.personalidad['nombre']}")
        print(f"   • Rol: {self.config.personalidad['rol']}")
        print(f"   • Especialidad: {self.config.personalidad['especialidad']}")
        print(f"   • Tono: {self.config.personalidad['tono']}")
        print(f"   • Historial activo: {len(self.historial_conversacion)//2} conversaciones")
    
    def limpiar_historial(self):
        """Limpia el historial de conversación"""
        self.historial_conversacion = []
        print("🧹 Historial de conversación limpiado.")
    
    def cambiar_personalidad(self):
        """Permite cambiar algunos aspectos de la personalidad"""
        print("\n🎭 Personalización del Chatbot")
        print("Deja vacío para mantener el valor actual")
        
        nuevo_nombre = input(f"Nombre actual: {self.config.personalidad['nombre']}\nNuevo nombre: ").strip()
        if nuevo_nombre:
            self.config.personalidad['nombre'] = nuevo_nombre
        
        nuevo_rol = input(f"Rol actual: {self.config.personalidad['rol']}\nNuevo rol: ").strip()
        if nuevo_rol:
            self.config.personalidad['rol'] = nuevo_rol
            
        nueva_especialidad = input(f"Especialidad actual: {self.config.personalidad['especialidad']}\nNueva especialidad: ").strip()
        if nueva_especialidad:
            self.config.personalidad['especialidad'] = nueva_especialidad
        
        # Actualizar sistema prompt
        self.config.sistema_prompt = f"""
        Eres {self.config.personalidad['nombre']}, {self.config.personalidad['rol']}.
        Tu tono de comunicación es {self.config.personalidad['tono']}.
        Te especializas en {self.config.personalidad['especialidad']}.
        Siempre respondes en {self.config.personalidad['idioma']}.
        
        Comportamientos específicos:
        - Sé conciso pero completo en tus respuestas
        - Si no sabes algo, admítelo honestamente
        - Ofrece ejemplos cuando sea útil
        - Mantén un tono amigable y profesional
        
        Responde de manera natural y conversacional.
        """
        
        print("✅ Personalidad actualizada!")
        self.limpiar_historial()  # Limpiar historial para aplicar cambios

def mostrar_comandos():
    """Muestra los comandos disponibles"""
    comandos = {
        "/help": "Muestra esta ayuda",
        "/info": "Información del chatbot",
        "/limpiar": "Limpia el historial de conversación",
        "/personalizar": "Cambia la personalidad del chatbot",
        "/test": "Prueba la conexión con la API",
        "/salir": "Termina el programa"
    }
    
    print("\n📋 Comandos disponibles:")
    for comando, descripcion in comandos.items():
        print(f"   {comando:<15} - {descripcion}")
    print()

def main():
    # Crear instancia del chatbot personalizado
    chatbot = ChatbotPersonalizado()
    
    print("="*60)
    print("🤖 CHATBOT PERSONALIZADO CON DEEPSEEK")
    print("="*60)
    
    chatbot.mostrar_info_chatbot()
    print("\n💡 Escribe '/help' para ver todos los comandos disponibles")
    print("-" * 60)
    
    while True:
        try:
            mensaje_usuario = input(f"\n👤 Tú: ").strip()
            
            # Comandos especiales
            if mensaje_usuario.lower() in ['/salir', 'salir', 'exit', 'quit']:
                print(f"\n🤖 {chatbot.config.personalidad['nombre']}: ¡Hasta luego! 👋")
                break
                
            elif mensaje_usuario.lower() in ['/help', 'help']:
                mostrar_comandos()
                continue
                
            elif mensaje_usuario.lower() in ['/info', 'info']:
                chatbot.mostrar_info_chatbot()
                continue
                
            elif mensaje_usuario.lower() in ['/limpiar', 'limpiar']:
                chatbot.limpiar_historial()
                continue
                
            elif mensaje_usuario.lower() in ['/personalizar', 'personalizar']:
                chatbot.cambiar_personalidad()
                continue
                
            elif mensaje_usuario.lower() in ['/test', 'test']:
                print("🔍 Probando conexión...")
                test_response = chatbot.enviar_mensaje("Hola, preséntate brevemente")
                print(f"🤖 {chatbot.config.personalidad['nombre']}: {test_response}")
                continue
                
            if not mensaje_usuario:
                print("💬 Por favor, escribe un mensaje o usa '/help' para ver los comandos.")
                continue
            
            # Enviar mensaje normal
            respuesta = chatbot.enviar_mensaje(mensaje_usuario)
            print(f"\n🤖 {chatbot.config.personalidad['nombre']}: {respuesta}")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print(f"\n\n🤖 {chatbot.config.personalidad['nombre']}: ¡Hasta luego! 👋")
            break
        except Exception as e:
            print(f"❌ Error en la aplicación: {e}")

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import requests
        print("✅ Módulo requests cargado correctamente")
    except ImportError:
        print("❌ Error: El módulo requests no está instalado")
        print("📦 Ejecuta: pip install requests")
        exit(1)
    
    main()

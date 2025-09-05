import streamlit as st
import requests
import json
from datetime import datetime
import time

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
        }
        
        # Sistema de prompt personalizable
        self.sistema_prompt = f"""
        Eres {self.personalidad['nombre']}, {self.personalidad['rol']}.
        Tu tono de comunicación es {self.personalidad['tono']}.
        Te especializas en {self.personalidad['especialidad']}.
        Siempre respondes en {self.personalidad['idioma']}.
        
        Comportamientos específicos:
        - Sé conciso pero completo en tus respuestas.
        - Si no sabes algo, admítelo honestamente.
        - Ofrece ejemplos cuando sea útil.
        - Mantén un tono amigable y profesional.
        
        Responde de manera natural y conversacional.
        """

class ChatbotPersonalizado:
    def __init__(self):
        self.config = ChatbotConfig()
        self.max_historial = 10  # Mantiene las últimas 10 interacciones
        
    def agregar_al_historial(self, rol, contenido):
        """Mantiene un historial de conversación para contexto"""
        if "historial_conversacion" not in st.session_state:
            st.session_state.historial_conversacion = []
            
        st.session_state.historial_conversacion.append({"role": rol, "content": contenido})
        
        # Limitar el tamaño del historial
        if len(st.session_state.historial_conversacion) > self.max_historial * 2:
            st.session_state.historial_conversacion = st.session_state.historial_conversacion[-self.max_historial * 2:]
    
    def preparar_mensajes(self, mensaje_usuario):
        """Prepara los mensajes incluyendo el sistema prompt y el historial"""
        mensajes = [{"role": "system", "content": self.config.sistema_prompt}]
        
        # Agregar historial de conversación
        if "historial_conversacion" in st.session_state:
            mensajes.extend(st.session_state.historial_conversacion)
        
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
            'temperature': 0.9,
            'max_tokens': 5000,
        }
        
        try:
            response = requests.post(self.config.API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                respuesta = response_data['choices'][0]['message']['content']
                
                # Agregar al historial
                self.agregar_al_historial("user", mensaje_usuario)
                self.agregar_al_historial("assistant", respuesta)
                
                return respuesta, None
            else:
                return None, f"Respuesta inesperada de la API: {response_data}"
                
        except requests.exceptions.ConnectionError:
            return None, "❌ Error: No se puede conectar a la API. Verifica tu conexión a internet."
        except requests.exceptions.Timeout:
            return None, "⏰ Error: La solicitud tardó demasiado tiempo. Inténtalo de nuevo."
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                return None, "🔑 Error: API Key inválida o expirada."
            elif err.response.status_code == 429:
                return None, "📊 Error: Has excedido el límite de solicitudes. Espera un momento."
            else:
                return None, f"❌ Error de la API ({err.response.status_code})"
        except Exception as e:
            return None, f"❌ Error inesperado: {e}"

# Inicializar el chatbot
@st.cache_resource
def inicializar_chatbot():
    return ChatbotPersonalizado()

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="🤖 Chatbot Personal",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado para mejorar la apariencia
    st.markdown("""
    <style>
        /* Importar fuentes modernas */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .main-header {
            text-align: center;
            padding: 2.5rem 1rem;
            background: linear-gradient(135deg, #0066CC 0%, #004499 35%, #0052A3 100%);
            color: white;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 102, 204, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .main-header h1 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .main-header p {
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            opacity: 0.9;
        }
        
        .chat-message {
            padding: 1.2rem;
            border-radius: 16px;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            font-family: 'Inter', sans-serif;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, #0066CC 0%, #0052A3 100%);
            color: white;
            margin-left: 15%;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 16px rgba(0, 102, 204, 0.4);
        }
        
        .bot-message {
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            color: #1E293B;
            border-left: 4px solid #0066CC;
            margin-right: 15%;
            border: 1px solid #E2E8F0;
        }
        
        .sidebar-info {
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            padding: 1.2rem;
            border-radius: 12px;
            margin: 1rem 0;
            border: 1px solid #E2E8F0;
        }
        
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin: 0.5rem 0;
            border: 1px solid #E2E8F0;
        }
        
        /* Personalización del sidebar */
        .css-1d391kg {
            background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
        }
        
        /* Botones personalizados */
        .stButton > button {
            border-radius: 10px;
            border: 1px solid #0066CC;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
        }
        
        /* Input personalizado */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #E2E8F0;
            font-family: 'Inter', sans-serif;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #0066CC;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
        }
        
        /* Métricas */
        .metric-container {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #E2E8F0;
            margin: 0.5rem 0;
        }
        
        .emoji-selector {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .emoji-option {
            padding: 0.5rem;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            background: white;
        }
        
        .emoji-option:hover {
            border-color: #0066CC;
            transform: scale(1.1);
        }
        
        .emoji-selected {
            border-color: #0066CC !important;
            background: rgba(0, 102, 204, 0.1) !important;
        }
        
        .welcome-message {
            text-align: center;
            padding: 2.5rem;
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            border-radius: 20px;
            margin: 2rem 0;
            border: 1px solid #E2E8F0;
            font-family: 'Inter', sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Inicializar chatbot
    chatbot = inicializar_chatbot()
    
    # Inicializar session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "historial_conversacion" not in st.session_state:
        st.session_state.historial_conversacion = []
    if "user_emoji" not in st.session_state:
        st.session_state.user_emoji = "👤"
    
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Chatbot Personal con DeepSeek</h1>
        <p>Tu asistente inteligente personalizado</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar con información y controles
    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        
        # Información del chatbot
        with st.expander("📊 Información del Bot", expanded=True):
            st.markdown(f"""
            **Nombre:** {chatbot.config.personalidad['nombre']}  
            **Rol:** {chatbot.config.personalidad['rol']}  
            **Especialidad:** {chatbot.config.personalidad['especialidad']}  
            **Tono:** {chatbot.config.personalidad['tono']}  
            **Conversaciones:** {len(st.session_state.historial_conversacion)//2}
            """)
        
        # Personalización rápida
        with st.expander("🎭 Personalización", expanded=False):
            # Selector de emoji para usuario
            st.markdown("**👤 Tu Avatar:**")
            emojis_usuario = ["👤", "😊", "🙂", "😎", "🤓", "👨‍💻", "👩‍💻", "🧑‍🎓", "👨‍🎓", "👩‍🎓", "🤵", "👸", "🦸‍♂️", "🦸‍♀️", "🧙‍♂️", "🧙‍♀️"]
            
            # Crear una cuadrícula de emojis
            cols = st.columns(4)
            for i, emoji in enumerate(emojis_usuario):
                with cols[i % 4]:
                    if st.button(emoji, key=f"emoji_{i}", 
                               help=f"Seleccionar {emoji} como tu avatar",
                               use_container_width=True):
                        st.session_state.user_emoji = emoji
                        st.success(f"Avatar cambiado a {emoji}")
                        st.rerun()
            
            st.markdown(f"**Avatar actual:** {st.session_state.user_emoji}")
            
            st.markdown("---")
            st.markdown("**🤖 Personalidad del Bot:**")
            nuevo_nombre = st.text_input("Nombre del bot", value=chatbot.config.personalidad['nombre'])
            nuevo_rol = st.text_input("Rol", value=chatbot.config.personalidad['rol'])
            nueva_especialidad = st.text_input("Especialidad", value=chatbot.config.personalidad['especialidad'])
            
            if st.button("🔄 Actualizar Personalidad", type="primary"):
                chatbot.config.personalidad['nombre'] = nuevo_nombre
                chatbot.config.personalidad['rol'] = nuevo_rol
                chatbot.config.personalidad['especialidad'] = nueva_especialidad
                
                # Actualizar sistema prompt
                chatbot.config.sistema_prompt = f"""
                Eres {chatbot.config.personalidad['nombre']}, {chatbot.config.personalidad['rol']}.
                Tu tono de comunicación es {chatbot.config.personalidad['tono']}.
                Te especializas en {chatbot.config.personalidad['especialidad']}.
                Siempre respondes en {chatbot.config.personalidad['idioma']}.
                
                Comportamientos específicos:
                - Sé conciso pero completo en tus respuestas
                - Si no sabes algo, admítelo honestamente
                - Ofrece ejemplos cuando sea útil
                - Mantén un tono amigable y profesional
                
                Responde de manera natural y conversacional.
                """
                
                st.success("✅ Personalidad actualizada!")
                st.rerun()
        
        # Controles
        st.markdown("## 🛠️ Controles")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 Limpiar", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.session_state.historial_conversacion = []
                st.success("¡Limpiado!")
                st.rerun()
        
        with col2:
            if st.button("🔍 Probar", use_container_width=True):
                with st.spinner("Probando..."):
                    respuesta, error = chatbot.enviar_mensaje("Hola, preséntate brevemente")
                    if error:
                        st.error("❌ Error")
                    else:
                        st.success("✅ Conectado")
        
        # Métricas mejoradas
        st.markdown("## 📈 Estadísticas")
        
        # Métricas en cards personalizadas
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="margin:0; color:#0066CC;">💬 {len(st.session_state.messages)}</h3>
            <p style="margin:0; color:#64748B;">Mensajes</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="margin:0; color:#0066CC;">🧠 {len(st.session_state.historial_conversacion)//2}</h3>
            <p style="margin:0; color:#64748B;">Contexto</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="margin:0; color:#0066CC;">{st.session_state.user_emoji}</h3>
            <p style="margin:0; color:#64748B;">Tu Avatar</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Área principal del chat
    st.markdown("## 💬 Conversación")
    
    # Contenedor para los mensajes
    chat_container = st.container()
    
    # Mostrar mensajes existentes
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>{st.session_state.user_emoji} Tú:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 {chatbot.config.personalidad['nombre']}:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Input para nuevo mensaje
    st.markdown("---")
    
    # Crear columnas para el input y botón
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        mensaje_usuario = st.text_input(
            "Escribe tu mensaje aquí...",
            key="user_input",
            placeholder="¿En qué puedo ayudarte hoy?"
        )
    
    with col2:
        enviar = st.button("📤 Enviar", type="primary")
    
    with col3:
        ejemplo = st.button("💡 Ejemplo")
    
    # Procesar mensaje
    if enviar and mensaje_usuario:
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": mensaje_usuario})
        
        # Mostrar mensaje del usuario inmediatamente
        with chat_container:
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>{st.session_state.user_emoji} Tú:</strong><br>
                {mensaje_usuario}
            </div>
            """, unsafe_allow_html=True)
        
        # Obtener respuesta del bot
        with st.spinner(f"🤖 {chatbot.config.personalidad['nombre']} está pensando..."):
            respuesta, error = chatbot.enviar_mensaje(mensaje_usuario)
            
            if error:
                st.error(error)
            else:
                # Agregar respuesta del bot
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
                
                # Mostrar respuesta con efecto de escritura
                with chat_container:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 {chatbot.config.personalidad['nombre']}:</strong><br>
                        {respuesta}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Limpiar input y rerun
        st.rerun()
    
    # Botón de ejemplo
    if ejemplo:
        ejemplos = [
            "¿Qué puedes hacer por mí?",
            "Explícame algo interesante sobre inteligencia artificial",
            "¿Cómo puedo ser más productivo?",
            "Cuéntame un dato curioso",
            "¿Qué opinas sobre el futuro de la tecnología?"
        ]
        import random
        mensaje_ejemplo = random.choice(ejemplos)
        st.session_state.user_input = mensaje_ejemplo
        st.rerun()
    
    # Mensajes de bienvenida si no hay conversación
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="welcome-message">
            <h3>👋 ¡Hola! Soy {chatbot.config.personalidad['nombre']}</h3>
            <p style="font-size: 1.1em; color: #475569; margin-bottom: 1.5rem;">
                Tu avatar actual es <strong>{st.session_state.user_emoji}</strong> - puedes cambiarlo en la barra lateral
            </p>
            <p style="color: #64748B;">Puedes preguntarme lo que quieras. Estoy aquí para ayudarte con:</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1.5rem 0;">
                <div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">
                    <strong style="color: #0066CC;">📚 Responder preguntas</strong><br>
                    <span style="color: #64748B;">Información general y específica</span>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">
                    <strong style="color: #0066CC;">✅ Tareas cotidianas</strong><br>
                    <span style="color: #64748B;">Organización y productividad</span>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">
                    <strong style="color: #0066CC;">💡 Consejos útiles</strong><br>
                    <span style="color: #64748B;">Sugerencias personalizadas</span>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">
                    <strong style="color: #0066CC;">💬 Conversaciones</strong><br>
                    <span style="color: #64748B;">Charlas interesantes</span>
                </div>
            </div>
            <p style="background: rgba(0, 102, 204, 0.1); padding: 1rem; border-radius: 10px; border-left: 4px solid #0066CC;">
                <strong>💡 Tip:</strong> Usa el botón "💡 Ejemplo" para ver preguntas de muestra
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; padding: 1.5rem; font-family: 'Inter', sans-serif;">
        <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">
            🤖 <strong style="color: #0066CC;">Chatbot Personal</strong> con DeepSeek API | 
            Desarrollado con ❤️ usando <strong style="color: #0066CC;">Streamlit</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

import streamlit as st
import requests
import json
from datetime import datetime
import time

class ChatbotConfig:
    def __init__(self):
        self.API_KEY = 'sk-53751d5c6f344a5dbc0571de9f51313e'
        self.API_URL = 'https://api.deepseek.com/v1/chat/completions'
        self.modelo = 'deepseek-chat'
        
        self.personalidad = {
            "nombre": "Asistente Personal",
            "rol": "un asistente útil y amigable",
            "tono": "profesional pero cercano",
            "especialidad": "ayudar con preguntas generales y tareas cotidianas",
            "idioma": "español",
        }
        

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
        self.max_historial = 10 
        
    def agregar_al_historial(self, rol, contenido):
        """Mantiene un historial de conversación para contexto"""
        if "historial_conversacion" not in st.session_state:
            st.session_state.historial_conversacion = []
            
        st.session_state.historial_conversacion.append({"role": rol, "content": contenido})
        

        if len(st.session_state.historial_conversacion) > self.max_historial * 2:
            st.session_state.historial_conversacion = st.session_state.historial_conversacion[-self.max_historial * 2:]
    
    def preparar_mensajes(self, mensaje_usuario):
        """Prepara los mensajes incluyendo el sistema prompt y el historial"""
        mensajes = [{"role": "system", "content": self.config.sistema_prompt}]
        

        if "historial_conversacion" in st.session_state:
            mensajes.extend(st.session_state.historial_conversacion)
        

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
            'max_tokens': 2000,
        }
        
        try:
            response = requests.post(self.config.API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'choices' in response_data and len(response_data['choices']) > 0:
                respuesta = response_data['choices'][0]['message']['content']
                

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


@st.cache_resource
def inicializar_chatbot():
    return ChatbotPersonalizado()

def main():

    st.set_page_config(
        page_title="🤖 Chatbot Personal",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: #669bbc;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 20%;
        }
        
        .bot-message {
            background: #003049;
            border-left: 4px solid #667eea;
            margin-right: 20%;
        }
        
        .sidebar-info {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)
    

    chatbot = inicializar_chatbot()
    

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "historial_conversacion" not in st.session_state:
        st.session_state.historial_conversacion = []
    

    st.markdown("""
    <div class="main-header">
        <h1>🤖 Chatbot Personal con DeepSeek</h1>
        <p>Tu asistente inteligente personalizado</p>
    </div>
    """, unsafe_allow_html=True)
    

    with st.sidebar:
        st.markdown("## ⚙️ Configuración")
        
  
        with st.expander("📊 Información del Bot", expanded=True):
            st.markdown(f"""
            **Nombre:** {chatbot.config.personalidad['nombre']}  
            **Rol:** {chatbot.config.personalidad['rol']}  
            **Especialidad:** {chatbot.config.personalidad['especialidad']}  
            **Tono:** {chatbot.config.personalidad['tono']}  
            **Conversaciones:** {len(st.session_state.historial_conversacion)//2}
            """)
        

        with st.expander("🎭 Personalización Rápida"):
            nuevo_nombre = st.text_input("Nombre del bot", value=chatbot.config.personalidad['nombre'])
            nuevo_rol = st.text_input("Rol", value=chatbot.config.personalidad['rol'])
            nueva_especialidad = st.text_input("Especialidad", value=chatbot.config.personalidad['especialidad'])
            
            if st.button("🔄 Actualizar Personalidad"):
                chatbot.config.personalidad['nombre'] = nuevo_nombre
                chatbot.config.personalidad['rol'] = nuevo_rol
                chatbot.config.personalidad['especialidad'] = nueva_especialidad
                
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
        
        st.markdown("## 🛠️ Controles")
        
        if st.button("🧹 Limpiar Conversación", type="secondary"):
            st.session_state.messages = []
            st.session_state.historial_conversacion = []
            st.success("Conversación limpiada!")
            st.rerun()
        
        if st.button("🔍 Probar Conexión"):
            with st.spinner("Probando conexión..."):
                respuesta, error = chatbot.enviar_mensaje("Hola, preséntate brevemente")
                if error:
                    st.error(error)
                else:
                    st.success("¡Conexión exitosa!")
                    st.info(respuesta)
        
    
        st.markdown("## 📈 Estadísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mensajes", len(st.session_state.messages))
        with col2:
            st.metric("Contexto", len(st.session_state.historial_conversacion)//2)
    
    st.markdown("## 💬 Conversación")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Tú:</strong><br>
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
    
    st.markdown("---")
    
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
    
    if enviar and mensaje_usuario:
        st.session_state.messages.append({"role": "user", "content": mensaje_usuario})
        
        with chat_container:
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 Tú:</strong><br>
                {mensaje_usuario}
            </div>
            """, unsafe_allow_html=True)
        
        with st.spinner(f"🤖 {chatbot.config.personalidad['nombre']} está pensando..."):
            respuesta, error = chatbot.enviar_mensaje(mensaje_usuario)
            
            if error:
                st.error(error)
            else:
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
                
                with chat_container:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 {chatbot.config.personalidad['nombre']}:</strong><br>
                        {respuesta}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.rerun()
    
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
    
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin: 2rem 0;">
            <h3>👋 ¡Hola! Soy tu asistente personal</h3>
            <p>Puedes preguntarme lo que quieras. Estoy aquí para ayudarte con:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>Responder preguntas generales</li>
                <li>Ayudar con tareas cotidianas</li>
                <li>Dar consejos y sugerencias</li>
                <li>Mantener conversaciones interesantes</li>
            </ul>
            <p><strong>💡 Tip:</strong> Usa el botón "💡 Ejemplo" para ver preguntas de muestra</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748B; padding: 1.5rem; font-family: 'Inter', sans-serif;">
        <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); padding: 1rem; border-radius: 12px; border: 1px solid #E2E8F0;">
            🤖 <strong style="color: #0066CC;">Chatbot Personal</strong> con DeepSeek API | 
            Desarrollado con ❤️  usando <strong style="color: #0066CC;">Streamlit</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

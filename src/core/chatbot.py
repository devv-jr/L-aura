# src/core/chatbot.py
import asyncio
from hugchat import hugchat
from hugchat.login import Login
import os
import logging
from pathlib import Path
from typing import Generator, Optional, Tuple, List

from src.core.tts import TextToSpeech
from src.config.settings import EMAIL, PASSWD, COOKIE_PATH

DEFAULT_SYSTEM_PROMPT = """Eres un asistente amigable y servicial. Tu objetivo es ayudar a los usuarios
de manera clara y precisa, manteniendo siempre un tono profesional pero cercano."""

DEFAULT_MODEL_INDEX = 6

class HuggyCore:
    def __init__(self):
        self.email = EMAIL
        self.password = PASSWD
        self.cookie_dir = COOKIE_PATH
        self.chatbot = self._initialize_chatbot()
        self.current_conversation = None
        self.available_models = []
        self._load_available_models()
        self.tts = TextToSpeech()

        # Verificar modelo predeterminado
        if DEFAULT_MODEL_INDEX < len(self.available_models):
            self.set_model(DEFAULT_MODEL_INDEX)
        else:
            logging.warning("Índice de modelo predeterminado no válido")

    def _initialize_chatbot(self) -> hugchat.ChatBot:
        try:
            sign = Login(self.email, self.password)
            cookies = sign.login(cookie_dir_path=str(self.cookie_dir), save_cookies=True)
            return hugchat.ChatBot(cookies=cookies.get_dict())
        except Exception as e:
            raise Exception(f"Error initializing chatbot: {str(e)}")

    def _get_available_models(self) -> List[str]:
        """Obtiene la lista de modelos disponibles."""
        try:
            return self.chatbot.get_available_llm_models()
        except Exception as e:
            logging.error(f"Error getting available models: {str(e)}")
            return []

    def set_model(self, model_index: int) -> bool:
        """Cambia al modelo especificado por su índice."""
        try:
            if 0 <= model_index < len(self.available_models):
            # Cambiar el modelo
                self.chatbot.switch_llm(model_index)
            
            # Crear nueva conversación para aplicar el cambio
                self.chatbot.new_conversation(switch_to=True)
            
            # Verificar el modelo en la nueva conversación
                info = self.chatbot.get_conversation_info()
                if info and info.model == self.available_models[model_index]:
                    logging.info(f"Modelo cambiado exitosamente a: {self.current_model}")
                    return True
                else:
                    logging.error("El modelo no se cambió correctamente")
                    return False
            else:
                logging.error(f"Índice de modelo inválido: {model_index}")
                return False
        except Exception as e:
            logging.error(f"Error al cambiar de modelo: {str(e)}", exc_info=True)  # Detalles del error
            return False

    def create_new_assistant(self, 
                           system_prompt: str = DEFAULT_SYSTEM_PROMPT,
                           assistant_id: Optional[str] = None) -> None:
        """
        Crea una nueva conversación con un prompt de sistema personalizado
        o un ID de asistente específico.
        """
        try:
            # Si se proporciona un ID de asistente, úsalo
            if assistant_id:
                self.chatbot.new_conversation(
                    assistant=assistant_id,
                    switch_to=True
                )
            else:
                # Crear nueva conversación con prompt personalizado
                self.chatbot.new_conversation(switch_to=True)
                # Establecer el prompt de sistema
                self.set_system_prompt(system_prompt)
            
            self.current_conversation = self.chatbot.get_conversation_info()
            return True
        except Exception as e:
            logging.error(f"Error creating new assistant: {str(e)}")
            return False

    def set_system_prompt(self, prompt: str) -> bool:
        """Establece un nuevo prompt de sistema para la conversación actual."""
        try:
            # Algunos modelos pueden requerir un formato específico
            formatted_prompt = f"System: {prompt}\nAssistant: Entendido, seguiré esas instrucciones."
            self.send_message(formatted_prompt)
            return True
        except Exception as e:
            logging.error(f"Error setting system prompt: {str(e)}")
            return False

    def get_conversation_info(self) -> dict:
        """Obtiene información sobre la conversación actual."""
        if self.current_conversation:
            return {
                "id": self.current_conversation.id,
                "title": self.current_conversation.title,
                "model": self.current_conversation.model,
                "system_prompt": self.current_conversation.system_prompt
            }
        return None

    def _load_available_models(self) -> None:
        """Carga y verifica los modelos disponibles."""
        try:
            self.available_models = self.chatbot.get_available_llm_models()
            logging.info(f"Modelos disponibles: {self.available_models}")
        
            if not self.available_models:
                raise ValueError("No se encontraron modelos disponibles")
        
        except Exception as e:
            logging.error(f"Error cargando modelos: {str(e)}", exc_info=True)
            self.available_models = []

    def send_message(
        self,
        message: str,
        stream: bool = False,
        web_search: bool = False
    ) -> Generator | Tuple[str, list]:
        response = self.chatbot.chat(
            message,
            stream=stream,
            web_search=web_search
        )
        
        if stream:
            return response
        else:
            result = response.wait_until_done()
            files = response.get_files_created()
            return result, files

    def send_message_with_tts(
        self,
        message: str,
        stream: bool = False,
        web_search: bool = False,
        generate_audio: bool = False
    ) -> Tuple[str, Optional[str]]:
        response, files = self.send_message(message, stream=stream, web_search=web_search)

        if generate_audio:
            # Generar archivo de audio con la respuesta
            audio_file_name = f"response_{hash(message)}.mp3"
            audio_path = asyncio.run(self.tts.generate_audio(response, audio_file_name))
            return response, audio_path
        
        return response, None

    
    @property
    def current_model(self) -> str:
        """Propiedad para obtener el modelo actual de forma dinámica"""
        info = self.chatbot.get_conversation_info()
        return info.model if info else None

    def list_models(self) -> List[str]:
        """Ahora retorna los nombres reales de los modelos (para mejor manejo)"""
        return self.available_models.copy()
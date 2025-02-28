import asyncio
from edge_tts import Communicate
from pathlib import Path

class TextToSpeech:
    def __init__(self, voice: str = "es-MX-DaliaNeural", output_dir: str = "data/cache"):
        """
        Inicializa el sistema de TTS.
        
        :param voice: Voz a utilizar (por defecto, una voz en español).
        :param output_dir: Directorio donde se guardarán los archivos de audio generados.
        """
        self.voice = voice
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_audio(self, text: str, output_file: str) -> str:
        """
        Genera un archivo de audio a partir de un texto.
        
        :param text: Texto a convertir en audio.
        :param output_file: Nombre del archivo de salida (sin ruta).
        :return: Ruta completa del archivo generado.
        """
        output_path = self.output_dir / output_file
        communicate = Communicate(text, self.voice)
        
        try:
            await communicate.save(str(output_path))
            return str(output_path)
        except Exception as e:
            raise RuntimeError(f"Error generating TTS audio: {str(e)}")
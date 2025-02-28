from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.chatbot import HuggyCore
from src.core.tts import TextToSpeech

# Inicializamos la aplicación FastAPI y el chatbot
app = FastAPI(title="AURA API", description="API para el chatbot AURA")
chatbot = HuggyCore()
tts = TextToSpeech()

# Modelos para estructurar las solicitudes entrantes
class CommandRequest(BaseModel):
    command: str
    user_id: str | None = None
    generate_audio: bool = False
    web_search: bool = False
    stream: bool = False

class ModelRequest(BaseModel):
    model_index: int

# Endpoint para procesar comandos de texto
@app.post("/api/command")
async def handle_command(request: CommandRequest):
    try:
        response, audio_path = chatbot.send_message_with_tts(
            message=request.command,
            stream=request.stream,
            web_search=request.web_search,
            generate_audio=request.generate_audio
        )
        
        result = {"response": response}
        if audio_path:
            result["audio_file"] = audio_path
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando el comando: {str(e)}")

# Endpoint para generar audio a partir de texto
@app.post("/api/tts")
async def generate_tts(request: CommandRequest):
    try:
        audio_file_name = f"tts_{hash(request.command)}.mp3"
        audio_path = await tts.generate_audio(request.command, audio_file_name)
        return {"audio_file": audio_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando audio: {str(e)}")

# Endpoint para cambiar el modelo del chatbot
@app.post("/api/change_model")
async def change_model(request: ModelRequest):
    try:
        success = chatbot.set_model(request.model_index)
        if not success:
            raise HTTPException(status_code=400, detail="No se pudo cambiar el modelo")
        return {"message": "Modelo cambiado exitosamente", "current_model": chatbot.current_model}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cambiando el modelo: {str(e)}")

# Endpoint para obtener los modelos disponibles
@app.get("/api/models")
async def get_models():
    try:
        return {"models": chatbot.list_models()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo modelos: {str(e)}")

# Punto de entrada para ejecutar la API directamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# src/cli_interface.py
import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from src.core.chatbot import HuggyCore, DEFAULT_SYSTEM_PROMPT

console = Console()

HUGGY_ART = """
    ╭──────────────────────────╮
    │   🤖 Huggy Assistant     │
    ╰──────────────────────────╯
"""

HELP_TEXT = """
Comandos disponibles:
/exit           - Salir del programa
/models         - Mostrar modelos disponibles
/switch <n>     - Cambiar al modelo número n
/new            - Crear nueva conversación
/prompt <texto> - Establecer nuevo prompt de sistema
/assistant <id> - Usar un asistente específico por ID
/info           - Mostrar información de la conversación actual
/tts [on|off]   - Habilitar/deshabilitar TTS
/help           - Mostrar esta ayuda
/clear          - Limpiar la pantalla
"""

class HuggyCLI:
    def __init__(self):
        self.core = HuggyCore()
        self.running = True
        self.console = Console()
        self.tts_enabled = False

    def run(self):
        """Punto de entrada principal del CLI"""
        parser = argparse.ArgumentParser(description=HUGGY_ART)
        parser.add_argument('-q', '--query', help="Consulta directa")
        parser.add_argument('-s', '--stream', action='store_true', help="Respuesta en stream")
        parser.add_argument('-w', '--web', action='store_true', help="Habilitar búsqueda web")
        
        args = parser.parse_args()
        
        try:
            if args.query:
                self._handle_direct_query(args)
            else:
                self._interactive_mode()
        except KeyboardInterrupt:
            console.print("\n[bold magenta]¡Hasta luego! 👋[/]")
        except Exception as e:
            console.print(f"\n[bold red]Error inesperado: {str(e)}[/]")
            
    def _handle_direct_query(self, args):
        """Maneja consultas directas desde la línea de comandos"""
        response = self.core.send_message(
            args.query,
            stream=args.stream,
            web_search=args.web
        )
        
        if args.stream:
            console.print("\n[bold green]Huggy:[/] ", end="")
            for chunk in response:
                console.print(chunk, end="", style="cyan")
            console.print()  # Nueva línea al final
        else:
            message, files = response
            console.print(f"\n[bold green]Huggy:[/] {message}")
            self._show_files(files)

    def _process_command(self, command: str) -> bool:
        """Procesa comandos especiales que empiezan con /"""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "/models":
            models = self.core.list_models()
            current_model = self.core.current_model
        
            model_list = []
            for i, model in enumerate(self.core.available_models):
                prefix = "➤" if model == current_model else " "
                model_list.append(f"{prefix} [bold cyan]{i}:[/] {model}")
        
            console.print(Panel(
                "\n".join(model_list),
                title=f"[bold green]Modelos Disponibles (Actual: {current_model})",
                border_style="blue"
            ))  
            return True

        elif cmd == "/switch":
            if not args:
                console.print(Panel(
                    "Uso: /switch <número_modelo>",
                    title="[bold red]Error",
                    border_style="red"
                ))
                return True
            
            try:
                index = int(args)
                if self.core.set_model(index):
                    new_model = self.core.current_model
                    console.print(Panel(
                        f"[bold green]Modelo cambiado a:[/] {new_model}",
                        title="✅ Éxito",
                        border_style="green"
                    ))
                else:
                    console.print(Panel(
                        f"Índice inválido. Usa /models para ver opciones válidas (0-{len(self.core.available_models)-1})",
                        title="[bold red]Error",
                        border_style="red"
                    ))
            except ValueError:
                console.print(Panel(
                    "Debe ser un número entero. Ejemplo: /switch 2",
                    title="[bold red]Error",
                    border_style="red"
                ))
            return True  # Este return debe estar al nivel del elif

        elif cmd == "/new":
            if self.core.create_new_assistant():
                console.print(Panel(
                    "Nueva conversación creada",
                    title="[bold green]Éxito",
                    border_style="green"
                ))
            return True

        elif cmd == "/prompt":
            if not args:
                console.print(Panel(
                    "Por favor proporciona un prompt",
                    title="[bold red]Error",
                    border_style="red"
                ))
                return True
            if self.core.set_system_prompt(args):
                console.print(Panel(
                    "Prompt de sistema actualizado",
                    title="[bold green]Éxito",
                    border_style="green"
                ))
            return True

        elif cmd == "/assistant":
            if not args:
                console.print(Panel(
                    "Por favor proporciona un ID de asistente",
                    title="[bold red]Error",
                    border_style="red"
                ))
                return True
            if self.core.create_new_assistant(assistant_id=args):
                console.print(Panel(
                    "Asistente cambiado exitosamente",
                    title="[bold green]Éxito",
                    border_style="green"
                ))
            return True

        elif cmd == "/info":
            info = self.core.get_conversation_info()
            if info:
                console.print(Panel(
                    "\n".join(f"{key}: {value}" for key, value in info.items()),
                    title="[bold blue]Información de la Conversación",
                    border_style="blue"
                ))
            else:
                console.print(Panel(
                    "No hay una conversación activa",
                    title="[bold yellow]Aviso",
                    border_style="yellow"
                ))
            return True

        elif cmd == "/help":
            console.print(Panel(
                HELP_TEXT,
                title="[bold blue]Ayuda",
                border_style="blue"
            ))
            return True
        elif cmd == "/tts":
            if args.lower() == "on":
                self.tts_enabled = True
                console.print(Panel(
                    "TTS habilitado",
                    title="[bold green]Éxito",
                    border_style="green"
                ))
            elif args.lower() == "off":
                self.tts_enabled = False
                console.print(Panel(
                    "TTS deshabilitado",
                    title="[bold yellow]Aviso",
                    border_style="yellow"
                ))
            else:
                console.print(Panel(
                    "Uso: /tts [on|off]",
                    title="[bold red]Error",
                    border_style="red"
                ))
            return True
        elif cmd == "/clear":
            console.clear()
            console.print(Markdown(HUGGY_ART))
            return True

        return False

    def _show_files(self, files):
        """Muestra los archivos generados en la respuesta"""
        if files:
            console.print(Panel(
                "\n".join(f"- {file}" for file in files),
                title="[bold blue]Archivos Generados",
                border_style="blue"
            ))

    def _process_input(self, user_input: str):
        """Procesa la entrada del usuario"""
        # Si es un comando, procesarlo
        if user_input.startswith('/'):
            if not self._process_command(user_input):
                console.print(Panel(
                    "Comando desconocido. Usa /help para ver los comandos disponibles",
                    title="[bold red]Error",
                    border_style="red"
                ))
            return

        # Si no es un comando, enviar como mensaje normal
        try:
            response, audio_path = self.core.send_message_with_tts(
                user_input,
                generate_audio=self.tts_enabled
            )
            console.print(f"\n[bold green]Huggy:[/] {response}")
            if audio_path:
                console.print(Panel(
                    f"Archivo de audio generado: {audio_path}",
                    title="[bold blue]TTS",
                    border_style="blue"
                ))
        except Exception as e:
            console.print(Panel(
                str(e),
                title="[bold red]Error",
                border_style="red"
            ))

    def _interactive_mode(self):
        """Inicia el modo interactivo del CLI"""
        console.print(Markdown(HUGGY_ART))
        console.print(Panel(
            "Escribe '/help' para ver los comandos disponibles\n"
            "Escribe '/exit' para salir",
            title="[bold magenta]Modo Interactivo",
            border_style="magenta"
        ))

        while self.running:
            try:
                user_input = Prompt.ask("[bold yellow]\nTú")
                
                if user_input.lower() == '/exit':
                    self.running = False
                    console.print("\n[bold magenta]¡Hasta luego! 👋[/]")
                    continue
                
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                self.running = False
                console.print("\n[bold magenta]¡Hasta luego! 👋[/]")
            except Exception as e:
                console.print(Panel(
                    str(e),
                    title="[bold red]Error Inesperado",
                    border_style="red"
                ))
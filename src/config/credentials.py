import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")

HF_EMAIL = os.getenv("HF_EMAIL")
HF_PASSWORD = os.getenv("HF_PASSWORD")

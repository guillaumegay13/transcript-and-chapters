import whisper
from datetime import timedelta
import openai
import os
# === Configuration ===
MP3_FILE = "ep1_enhanced.mp3"
TRANSCRIPT_FILE = "transcript_ep1.txt"
CHAPTERS_FILE = "chapters_ep1.txt"
MODEL_SIZE = "base"  # or "medium", "large" for better quality
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Set your OpenAI key here

# === Setup ===
openai.api_key = OPENAI_API_KEY
model = whisper.load_model(MODEL_SIZE)

print("Transcribing...")
result = model.transcribe(MP3_FILE)

# === Save full transcript ===
with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
    f.write(result["text"])
print(f"Transcript saved to {TRANSCRIPT_FILE}")

# === Prepare for AI chaptering ===
segments = result["segments"]

def format_timestamp(seconds):
    return str(timedelta(seconds=int(seconds)))

# Build a string with timestamps + text for clarity
transcript_with_timestamps = ""
for seg in segments:
    timestamp = format_timestamp(seg['start'])
    transcript_with_timestamps += f"[{timestamp}] {seg['text']}\n"

# === Ask GPT to split into chapters ===
print("Asking AI to generate chapters based on content...")
prompt = (
    "Tu es un expert en podcasts. Voici la transcription d'un épisode, avec les horodatages. "
    "Analyse le contenu et découpe l'épisode en chapitres pertinents. "
    "Pour chaque chapitre, donne l'horodatage de début (au format HH:MM:SS) et un titre court.\n\n"
    f"{transcript_with_timestamps}\n\n"
    "Réponds sous ce format :\n"
    "HH:MM:SS - Titre du chapitre"
)

response = openai.chat.completions.create(
    model="o4-mini-2025-04-16",  # Use GPT-4 if available, or stick with gpt-3.5-turbo
    messages=[{"role": "user", "content": prompt}]
)

chapters_text = response.choices[0].message.content.strip()

# === Save chapters ===
with open(CHAPTERS_FILE, "w", encoding="utf-8") as f:
    f.write(chapters_text)

print(f"Chapters saved to {CHAPTERS_FILE}")

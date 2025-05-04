import streamlit as st
import whisper
from datetime import timedelta
import openai
import os
import tempfile

# --- Helper Functions ---

def format_timestamp(seconds):
    """Formats seconds into HH:MM:SS."""
    return str(timedelta(seconds=int(seconds)))

@st.cache_resource # Cache the model loading
def load_whisper_model(model_size="base"):
    """Loads the Whisper model."""
    return whisper.load_model(model_size)

def transcribe_audio(model, audio_path):
    """Transcribes the audio file using Whisper."""
    try:
        result = model.transcribe(audio_path, fp16=False) # fp16=False for CPU compatibility
        return result
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return None

def generate_chapters(api_key, transcript_result):
    """Generates chapters using OpenAI based on the transcript."""
    if not api_key:
        st.error("OpenAI API key is required to generate chapters.")
        return None

    openai.api_key = api_key
    segments = transcript_result["segments"]

    # Build a string with timestamps + text
    transcript_with_timestamps = ""
    for seg in segments:
        timestamp = format_timestamp(seg['start'])
        transcript_with_timestamps += f"[{timestamp}] {seg['text']}\n"

    prompt = f"""Tu es un expert en podcasts. Voici la transcription d'un épisode, avec les horodatages. 
Analyse le contenu et découpe l'épisode en chapitres pertinents. 
Pour chaque chapitre, donne l'horodatage de début (au format HH:MM:SS) et un titre court.

{transcript_with_timestamps}

Réponds EXCLUSIVEMENT sous ce format (une ligne par chapitre, sans texte additionnel avant ou après):
HH:MM:SS - Titre du chapitre"""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo", # Using 3.5-turbo for wider availability, can be changed
            messages=[{"role": "user", "content": prompt}]
        )
        chapters_text = response.choices[0].message.content.strip()
        # Basic validation of the format
        lines = chapters_text.split('\n')
        if not all(line[8:11] == ' - ' for line in lines if len(line) > 11):
             st.warning("AI response format might be slightly off, but proceeding.")
        return chapters_text
    except openai.AuthenticationError:
        st.error("OpenAI Authentication Error: Please check your API key.")
        return None
    except Exception as e:
        st.error(f"Error calling OpenAI API: {e}")
        return None

# --- Streamlit UI ---

st.set_page_config(layout="wide")
st.title("🎙️ Podcast Transcript & Chapter Generator")

# --- Configuration Sidebar ---
with st.sidebar:
    st.header("Configuration")
    openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password", help="Your API key is used solely for chapter generation via the OpenAI API.")

    # model_size = st.selectbox("Whisper Model Size", ("tiny", "base", "small", "medium", "large"), index=1)
    # For simplicity and faster loading in a typical web context, let's fix the model size
    model_size = "base"
    st.info(f"Using Whisper model size: `{model_size}` (fixed for this app)")

    st.header("Instructions")
    st.markdown("""
    1.  Enter your OpenAI API Key (required only for chapter generation).
    2.  Upload your podcast MP3 file.
    3.  Select whether you want a transcript, chapters, or both.
    4.  Click 'Process Audio'.
    5.  Download your results.
    """)

# --- Main Area ---
st.header("Upload & Process")
uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

col1, col2 = st.columns(2)
with col1:
    generate_transcript = st.checkbox("Generate Transcript", value=True)
with col2:
    generate_chapters_flag = st.checkbox("Generate Chapters (Requires OpenAI Key)")

process_button = st.button("Process Audio", disabled=not uploaded_file)

if process_button:
    if not generate_transcript and not generate_chapters_flag:
        st.warning("Please select at least one output (Transcript or Chapters).")
    else:
        transcript_result = None
        transcript_text = ""
        chapters_text = ""

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_audio_path = tmp_file.name

        try:
            # --- Transcription ---
            if generate_transcript or generate_chapters_flag: # Transcription is needed for chapters too
                with st.spinner(f"Loading Whisper model ('{model_size}')..."):
                    model = load_whisper_model(model_size)
                with st.spinner(f"Transcribing audio with Whisper ('{model_size}')... Please wait."):
                    transcript_result = transcribe_audio(model, temp_audio_path)

                if transcript_result:
                    transcript_text = transcript_result["text"]
                    if generate_transcript:
                        st.subheader("📜 Transcript")
                        st.text_area("Full Transcript", transcript_text, height=300)
                        st.download_button(
                            label="Download Transcript (.txt)",
                            data=transcript_text,
                            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_transcript.txt",
                            mime="text/plain"
                        )

            # --- Chapter Generation ---
            if generate_chapters_flag and transcript_result:
                 if not openai_api_key:
                     st.error("OpenAI API Key needed for chapter generation is missing.")
                 else:
                    with st.spinner("Generating chapters with AI..."):
                        chapters_text = generate_chapters(openai_api_key, transcript_result)

                    if chapters_text:
                        st.subheader("📑 Chapters")
                        st.text_area("Generated Chapters", chapters_text, height=200)
                        st.download_button(
                            label="Download Chapters (.txt)",
                            data=chapters_text,
                            file_name=f"{os.path.splitext(uploaded_file.name)[0]}_chapters.txt",
                            mime="text/plain"
                        )

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        finally:
            # Clean up the temporary file
            if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

elif uploaded_file:
    st.info("Click 'Process Audio' to start.") 
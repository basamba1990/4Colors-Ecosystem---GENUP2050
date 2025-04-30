from openai import OpenAI
import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_audio(video_path: str) -> str:
    """Extrait l'audio d'une vidéo"""
    video = VideoFileClip(video_path)
    audio_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    video.audio.write_audiofile(audio_path, codec='pcm_s16le')
    return audio_path

def transcribe_audio(file_path: str) -> str:
    """Transcription audio/vidéo avec gestion d'erreurs"""
    try:
        if file_path.endswith((".mp4", ".mov")):
            file_path = extract_audio(file_path)
        
        with open(file_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
                language="fr"
            )
        return transcript
    except Exception as e:
        st.error(f"Erreur de transcription : {str(e)}")
        raise

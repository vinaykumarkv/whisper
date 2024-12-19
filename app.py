import streamlit as st
import whisper
import os
from pathlib import Path

# Load the Whisper model
model = whisper.load_model("base")

# Streamlit UI
st.title("Whisper Audio Transcription App")
st.write("Upload an audio file to transcribe and download as SRT.")

# Upload audio file
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])

if uploaded_file:
    # Save uploaded file temporarily
    audio_path = Path("temp_audio") / uploaded_file.name
    audio_path.parent.mkdir(exist_ok=True, parents=True)
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.audio(str(audio_path), format="audio/mp3", start_time=0)
    st.write("Transcribing...")

    # Process the audio with Whisper
    result = model.transcribe(str(audio_path))  # Convert Path to string

    # Display transcription
    st.subheader("Transcription")
    st.text(result["text"])

    # Generate SRT content
    srt_content = ""
    for segment in result["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        srt_content += f"{segment['id'] + 1}\n{start:.3f} --> {end:.3f}\n{text}\n\n"

    # Provide download link for SRT file
    srt_file_path = Path("temp_srt") / (audio_path.stem + ".srt")
    srt_file_path.parent.mkdir(exist_ok=True, parents=True)
    with open(srt_file_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    st.download_button(
        label="Download Transcription (SRT)",
        data=srt_content,
        file_name=f"{audio_path.stem}.srt",
        mime="text/plain",
    )

    # Cleanup temp files
    st.write("Cleaning up temporary files...")
    audio_path.unlink()  # Remove audio file
    srt_file_path.unlink()  # Remove SRT file

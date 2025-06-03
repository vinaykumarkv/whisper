import os
import streamlit as st
import streamlit.components.v1 as components
import whisper
from pathlib import Path
import uuid
import shutil
from datetime import timedelta
import imageio_ffmpeg

# Set ffmpeg path using imageio_ffmpeg
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ["PATH"]

# Load Whisper model
model = whisper.load_model("base")

# Streamlit UI
st.title("Convert Audio to SRT: Free Audio Transcription Made Easy")
st.write("""
Upload an audio file to transcribe and download as SRT.
Convert your audio files to SRT effortlessly with our Audio to SRT tool.
Experience fast and accurate audio transcription for all your needs today!
""")

# AdSense (this will only show if deployed on a site with proper setup)
ad_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4034435637284460"
     crossorigin="anonymous"></script>
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4034435637284460"
     data-ad-slot="1234567890"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""
components.html(ad_code, height=200)

# Upload audio file
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])

def format_srt_time(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    milliseconds = int((seconds - total_seconds) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

if uploaded_file:
    # Save uploaded file
    unique_id = uuid.uuid4().hex
    audio_path = Path("temp_audio") / f"{unique_id}_{uploaded_file.name}"
    audio_path.parent.mkdir(exist_ok=True, parents=True)
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.audio(str(audio_path), format="audio/mp3", start_time=0)
    st.write("Transcribing...")

    try:
        result = model.transcribe(str(audio_path))

        # Show full transcription
        st.subheader("Transcription")
        st.text_area("Transcribed Text", result["text"], height=300)

        # Generate SRT content
        srt_content = ""
        for segment in result["segments"]:
            start = format_srt_time(segment["start"])
            end = format_srt_time(segment["end"])
            text = segment["text"].strip()
            srt_content += f"{segment['id'] + 1}\n{start} --> {end}\n{text}\n\n"

        # Save SRT
        srt_file_path = Path("temp_srt") / f"{audio_path.stem}.srt"
        srt_file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(srt_file_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        st.download_button(
            label="Download Transcription (SRT)",
            data=srt_content,
            file_name=f"{audio_path.stem}.srt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")

    finally:
        shutil.rmtree("temp_audio", ignore_errors=True)
        shutil.rmtree("temp_srt", ignore_errors=True)

# Donation QR code
st.write("If you find this app useful, consider donating to support its development:")
st.image("payment.jpg", caption="Scan to donate via PayPal", width=200)

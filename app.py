import os
import streamlit as st
import streamlit.components.v1 as components
import whisper
from pathlib import Path
import uuid
import shutil
from datetime import timedelta
import imageio_ffmpeg

# Set ffmpeg path using imageio_ffmpeg (needed by whisper)
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

# AdSense (replace with your actual ad slot ID if needed)
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

def format_srt_time(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    milliseconds = int((seconds - total_seconds) * 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

# Upload audio file
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])

if uploaded_file:
    unique_id = uuid.uuid4().hex
    audio_dir = Path("temp_audio")
    srt_dir = Path("temp_srt")
    audio_dir.mkdir(exist_ok=True, parents=True)
    srt_dir.mkdir(exist_ok=True, parents=True)

    audio_path = audio_dir / f"{unique_id}_{uploaded_file.name}"
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Play audio (detect mime type from file extension)
    ext = audio_path.suffix.lower()
    mime_type = {
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4"
    }.get(ext, "audio/mp3")
    st.audio(str(audio_path), format=mime_type)

    st.write("Transcribing...")

    try:
        result = model.transcribe(str(audio_path))

        st.subheader("Transcription")
        st.text_area("Transcribed Text", result["text"], height=300)

        srt_content = ""
        for segment in result["segments"]:
            start = format_srt_time(segment["start"])
            end = format_srt_time(segment["end"])
            text = segment["text"].strip()
            srt_content += f"{segment['id'] + 1}\n{start} --> {end}\n{text}\n\n"

        srt_file_path = srt_dir / f"{audio_path.stem}.srt"
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
        # Cleanup only the files we created (keep the directories)
        try:
            if audio_path.exists():
                audio_path.unlink()
            if srt_file_path.exists():
                srt_file_path.unlink()
        except Exception as cleanup_err:
            st.warning(f"Could not clean up temp files: {cleanup_err}")

# Donation QR code
st.write("If you find this app useful, consider donating to support its development:")
st.image("payment.jpg", caption="Scan to donate via PayPal", width=200)

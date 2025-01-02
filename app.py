import streamlit as st
import streamlit.components.v1 as components
import whisper
from pathlib import Path
import os

# Load the Whisper model
model = whisper.load_model("base")

# Streamlit UI
st.title("Convert Audio to SRT: Free Audio Transcription Made Easy")
st.write("""Upload an audio file to transcribe and download as SRT.
          Convert your audio files to SRT effortlessly with our Audio to SRT tool.
          Experience fast and accurate audio transcription for all your needs today!""")

# Embed AdSense ad code
ad_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4034435637284460"
     crossorigin="anonymous"></script>
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-4034435637284460"
     data-ad-slot="XXXXXXXXXX"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""
components.html(ad_code, height=200)

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

    try:
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

    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")

    finally:
        # Cleanup temp files
        st.write("Cleaning up temporary files...")
        if audio_path.exists():
            audio_path.unlink()  # Remove audio file
        if srt_file_path.exists():
            srt_file_path.unlink()  # Remove SRT file

# Embed PayPal donation QR code image
st.write("If you find this app useful, consider donating to support its development:")
paypal_qr_code_path = "payment.jpg"  # Replace with the actual path to your QR code image
st.image(paypal_qr_code_path, caption="Scan to donate via PayPal", width=200)

import streamlit as st
import tempfile
import numpy as np
import soundfile as sf
from openai import OpenAI
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, RTCConfiguration, WebRtcMode
import av

# -------------------
# Setup
# -------------------
st.set_page_config(page_title="Forced Mic Test", layout="centered")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -------------------
# Audio Processor with Debug
# -------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = []
        self.frame_count = 0

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        self.buffer.append(audio)
        self.frame_count += 1
        return frame

# -------------------
# WebRTC Recorder with Forced Mic Access
# -------------------
st.title("🎤 Forced Mic Test with Debug")
st.markdown("Press **Start** → browser should immediately ask for mic permission.")

webrtc_ctx = webrtc_streamer(
    key="forced_mic_debug",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTCConfiguration({
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]},
            {
                "urls": [
                    "turn:openrelay.metered.ca:80",
                    "turn:openrelay.metered.ca:443",
                    "turn:openrelay.metered.ca:443?transport=tcp"
                ],
                "username": "openrelayproject",
                "credential": "openrelayproject"
            }
        ]
    }),
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": {"echoCancellation": True, "noiseSuppression": True}},
)

if webrtc_ctx and webrtc_ctx.state.playing and webrtc_ctx.audio_processor:
    st.info(f"🎤 Debug: WebRTC running. Frames captured: {webrtc_ctx.audio_processor.frame_count}, Buffer size: {len(webrtc_ctx.audio_processor.buffer)}")

    if st.button("Stop & Transcribe"):
        if webrtc_ctx.audio_processor.buffer:
            st.info(f"🎤 Debug: Concatenating {len(webrtc_ctx.audio_processor.buffer)} frames")
            audio_data = np.concatenate(webrtc_ctx.audio_processor.buffer)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                sf.write(tmpfile.name, audio_data, 44100)
                st.audio(tmpfile.name)
                with open(tmpfile.name, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                st.success(f"🎤 Transcribed: {transcript.text}")
        else:
            st.error("⚠️ Debug: Buffer empty. No audio data captured.")

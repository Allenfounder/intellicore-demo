import streamlit as st
import threading
import hashlib
import time
import requests
import numpy as np
from random import choice
from scipy.stats import ks_2samp
from transformers import pipeline

# ─── GUARD AUDIO IMPORTS ─────────────────────────────────────────────────────
try:
    import sounddevice as sd
    import speech_recognition as sr
    has_audio = True
except OSError:
    has_audio = False

# ─── CONFIG ─────────────────────────────────────────────────────────────────
API_URL = "https://demo.intellicore.ai"   # ← your real API endpoint
PASSWORD = "Stakeholder2025"

# ─── PAGE SETUP ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="IntelliCore AGI Demo", layout="wide")

# ─── PASSWORD GATE ───────────────────────────────────────────────────────────
def check_password():
    def encrypt(p): return hashlib.sha256(p.encode()).hexdigest()
    pwd = st.text_input("Demo Password:", type="password")
    if encrypt(pwd) != encrypt(PASSWORD):
        st.warning("🔒 Access denied")
        st.stop()

check_password()

# ─── BRANDING ─────────────────────────────────────────────────────────────────
st.image("https://intellicore.ai/assets/logo_dark.png", width=120)
st.title("🤖 IntelliCore AGI – Stakeholder Demo")

# ─── STATE ───────────────────────────────────────────────────────────────────
if 'last_decision' not in st.session_state:
    st.session_state['last_decision'] = None

# ─── TABS ────────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "► Home", "🛰 Agents", "📡 Telemetry",
    "🔄 Reflection", "🎤 Speech", "😊 Emotion", "⚠️ Drift"
])

# ─── HOME TAB ────────────────────────────────────────────────────────────────
with tabs[0]:
    st.header("Cortex Reasoning")
    question = st.text_input("Ask IntelliCore:", placeholder="Deploy drone to Area B?")
    if st.button("Submit to Cortex"):
        decision = choice([
            "Deploy drone to Area B for surveillance.",
            "Hold drone deployment, awaiting weather confirmation.",
            "Initiate data link with northern outpost."
        ])
        st.session_state['last_decision'] = decision
        st.success(f"🤖 Decision: {decision}")

    if st.session_state['last_decision']:
        st.markdown("**Ready to execute:**")
        exec_col, show_col = st.columns([1, 3])
        with exec_col:
            if st.button("Execute Decision"):
                cmd = st.session_state['last_decision']
                agent = (
                    "drone" if "drone" in cmd.lower() else
                    "humanoid" if "humanoid" in cmd.lower() else
                    "virtual"
                )
                try:
                    resp = requests.post(
                        f"{API_URL}/agent/{agent}",
                        json={"command": cmd},
                        timeout=5
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    st.success(f"✅ {agent.capitalize()} Response: {data.get('executed')}")
                except Exception:
                    mocks = {
                        "drone": "🛰 Mock: drone dispatched.",
                        "humanoid": "🧍 Mock: humanoid activated.",
                        "virtual": "💬 Mock: virtual agent responded."
                    }
                    st.info(mocks[agent])
        with show_col:
            st.write(f"> {st.session_state['last_decision']}")

# ─── AGENTS TAB ──────────────────────────────────────────────────────────────
with tabs[1]:
    st.header("Agent Command Center")
    c1, c2, c3 = st.columns(3)
    if c1.button("Send Drone"):
        st.info("🛰 Drone deployed to Area B")
    if c2.button("Activate Humanoid"):
        st.info("🧍 Humanoid assisting medical team")
    if c3.button("Contact Virtual"):
        st.success("💬 Virtual Agent says: 'All systems are operational.'")

# ─── TELEMETRY TAB ───────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown("### 📡 Live Agent Telemetry")
    telemetry_box = st.empty()

    if st.button("📶 Start Feed"):
        def stream():
            updates = [
                {"agent": "drone", "status": "Scanning", "zone": "Sector A"},
                {"agent": "humanoid", "status": "Assisting", "zone": "Zone B"},
                {"agent": "virtual", "status": "Reporting", "zone": "HQ"}
            ]
            for _ in range(10):
                telemetry_box.json(choice(updates))
                time.sleep(1)

        thread = threading.Thread(target=stream)
        thread.start()

# ─── REFLECTION TAB ─────────────────────────────────────────────────────────
with tabs[3]:
    st.header("Self-Reflection Logs")
    logs = [
        {"timestamp": "2025-04-15T12:01Z", "suggestion": "Refactor memory", "approved": True, "why": "Better recall"},
        {"timestamp": "2025-04-14T18:47Z", "suggestion": "Optimize path", "approved": True, "why": "Energy saving"}
    ]
    for e in logs:
        st.markdown(
            f"**{e['timestamp']}** – *{e['suggestion']}* "
            f"({'✅' if e['approved'] else '❌'})\n> {e['why']}"
        )

# ─── SPEECH TAB ─────────────────────────────────────────────────────────────
with tabs[4]:
    st.header("Speech-to-Text")
    if not has_audio:
        st.warning("🔇 Audio unavailable in this environment.")
    else:
        if st.button("Record & Transcribe"):
            recognizer = sr.Recognizer()
            with sd.InputStream(samplerate=16000, channels=1) as stream:
                st.info("Recording...")
                audio = stream.read(16000 * 5)[0]
            audio_data = sr.AudioData(np.array(audio).tobytes(), 16000, 2)
            try:
                text = recognizer.recognize_google(audio_data)
                st.success(f"🔊 {text}")
            except Exception as e:
                st.error(f"Transcription error: {e}")

# ─── EMOTION TAB ───────────────────────────────────────────────────────────
with tabs[5]:
    st.header("Emotion Analysis")
    user_text = st.text_area("Enter text to analyze:")
    if st.button("Analyze Emotion"):
        emo_pipe = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base"
        )
        result = emo_pipe(user_text)
        st.json(result)

# ─── DRIFT TAB ──────────────────────────────────────────────────────────────
with tabs[6]:
    st.header("Data Drift Detection")
    if st.button("Check Drift"):
        ref = np.random.normal(size=500)
        new = np.concatenate([ref, np.random.normal(loc=1.5, size=100)])
        stat, pvalue = ks_2samp(ref, new)
        st.write("Drift detected:", pvalue < 0.05)
        st.write("p-value:", round(pvalue, 4))

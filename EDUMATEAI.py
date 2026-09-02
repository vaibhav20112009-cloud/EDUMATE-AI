from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

import time
import re
# Google Gemini API (used automatically when GEMINI_API_KEY is available)
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None
import base64
import io
import json
import os
import uuid
from datetime import datetime

# Optional offline speech-to-text dependency.
# Install once with:
#   pip install faster-whisper
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except Exception:
    FASTER_WHISPER_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================


# ---- Persistent chat history ----
HISTORY_FILE = Path("edumate_chat_history.json")

def load_persistent_history():
    try:
        if HISTORY_FILE.exists():
            with HISTORY_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}

def save_persistent_history(history):
    try:
        with HISTORY_FILE.open("w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

st.set_page_config(
    page_title="EduMate AI Ultra Pro",
    page_icon="😎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# MODELS
# =========================================================

TEXT_MODELS = [
    "Gemini 3.6 Flash",
    "Gemini 3.5 Flash-Lite",
    "Gemini 3.7 Flash",
    "Gemini 3.5 Flash",
    "Gemini 3.1 Flash-Lite",
    "Gemini 2.5 Flash",
]

# Local Whisper model.
# "base" is a reasonable CPU starting point.
# After the first download, transcription works locally/offline.
WHISPER_MODEL_SIZE = "base"

HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edumate_history")
CHATS_FILE = os.path.join(HISTORY_DIR, "chats.json")
IMAGES_DIR = os.path.join(HISTORY_DIR, "images")

# =========================================================
# SAVING HISTORY
# =========================================================

# =========================================================
# DIRECTORIES
# =========================================================

os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

/* =====================================================
   MAIN HEADER
   ===================================================== */

.main-title {
    font-size: 2.55rem;
    font-weight: 800;
    margin-bottom: 3px;
}

.subtitle {
    color: #9aa4b2;
    font-size: 1.02rem;
    margin-bottom: 15px;
}


/* =====================================================
   SMALL CURRENT STATUS BOX
   ===================================================== */

.current-status-box {
    display: inline-block;
    padding: 7px 14px;
    margin: 3px 0 16px 0;
    border-radius: 10px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    font-size: 0.82rem;
    color: #d6dce4;
    line-height: 1.2;
}

.current-label {
    color: #8f98a7;
}


/* =====================================================
   MODE INFO
   ===================================================== */

.mode-info {
    padding: 12px 15px;
    border-radius: 13px;
    background: rgba(33,150,243,0.07);
    border: 1px solid rgba(33,150,243,0.17);
    margin-bottom: 18px;
    font-size: 0.91rem;
}


/* =====================================================
   MODE BUTTONS
   ===================================================== */

div.stButton > button {
    width: 100%;
    min-height: 100px;
    border-radius: 15px;
    font-weight: 700;
    font-size: 0.96rem;
    border: 1px solid rgba(255,255,255,0.10);
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(33,150,243,0.55);
    box-shadow: 0 6px 18px rgba(33,150,243,0.15);
}


/* =====================================================
   SIDEBAR
   ===================================================== */

/* =====================================================
   COLLAPSIBLE SIDEBAR -> FULL MAIN AREA
   ===================================================== */

/* Do not force a minimum width while the native Streamlit
   sidebar is collapsed. */
section[data-testid="stSidebar"] {
    width: 280px;
}

/* Keep the expanded sidebar at the same width. */
section[data-testid="stSidebar"][aria-expanded="true"] {
    width: 280px !important;
    min-width: 280px !important;
}

/* IMPORTANT:
   Do not set width/min-width to 0 here. Streamlit's own
   collapse mechanism will remove the sidebar from the
   layout and automatically give the main page the space. */

/* Let the main app use all available width. */
[data-testid="stAppViewContainer"] > .main {
    width: 100%;
    max-width: none !important;
}

.main .block-container {
    max-width: none !important;
    width: 100% !important;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* On smaller screens, use tighter padding. */
@media (max-width: 900px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

.sidebar-heading {
    font-size: 1.3rem;
    font-weight: 800;
}

.small-note {
    color: #8f98a7;
    font-size: 0.82rem;
}


/* =====================================================
   SELECTBOX SPACING
   ===================================================== */

section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {
    margin-bottom: 8px;
}


/* =====================================================
   CHAT
   ===================================================== */

[data-testid="stChatMessage"] {
    margin-bottom: 8px;
}

.response-actions {
    margin-top: 4px;
}

.history-card {
    padding: 9px 10px;
    border-radius: 10px;
    margin-bottom: 7px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.07);
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_class" not in st.session_state:
    st.session_state.selected_class = "Class 9"

if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "All Subjects"

if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = "Standard"

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "whisper_model" not in st.session_state:
    st.session_state.whisper_model = None

if "whisper_status" not in st.session_state:
    st.session_state.whisper_status = ""

if "history" not in st.session_state:
    st.session_state.history = {}

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

if "history_menu" not in st.session_state:
    st.session_state.history_menu = None




# =========================================================
# OPTIONS
# =========================================================

class_options = [
    "Class 6",
    "Class 7",
    "Class 8",
    "Class 9",
    "Class 10",
    "Class 11",
    "Class 12",
    "Ungraduated",
    "Pregraduated"
]

subject_options = [
    "All Subjects",
    "Mathematics",
    "Physics",
    "Chemistry",
    "Biology",
    "Computer Science",
    "Artificial Intelligence",
    "Robotics",
    "English",
    "Hindi",
    "History",
    "Geography",
    "Civics",
    "Economics",
    "General Knowledge (GK)",
    "Reasoning"
]

voice_languages = {
    "English (India)": "en",
    "Hindi (India)": "hi"
}

tts_languages = {
    "English (India)": "en-IN",
    "Hindi (India)": "hi-IN"
}

mode_descriptions = {
    "Smart Reasoning":
        "Step-by-step reasoning with clear logic and concepts.",

    "Maths Genius":
        "Math-focused solving with formulas, calculations and steps.",

    "Research":
        "Detailed, structured and deeper explanations.",

    "Standard":
        "Balanced mode for normal everyday study questions."
}


# =========================================================
# HISTORY FUNCTIONS
# =========================================================

def load_history():
    """Load saved chats from local JSON storage."""
    if not os.path.exists(CHATS_FILE):
        return {}

    try:
        with open(CHATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        return {}

    except Exception:
        return {}


def save_history(history):
    """Persist all chats locally."""
    temp_file = CHATS_FILE + ".tmp"

    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        os.replace(temp_file, CHATS_FILE)

    except Exception as e:
        st.warning(f"Could not save chat history: {e}")


def make_chat_title(messages):
    """Create a simple title from the first user message."""
    for message in messages:
        if message.get("role") == "user":
            text = message.get("content", "").strip()
            if text:
                text = " ".join(text.split())
                if len(text) > 42:
                    text = text[:42].rstrip() + "..."
                return text

    return "New Chat"


def create_chat():
    """Create a new local chat."""
    chat_id = str(uuid.uuid4())

    st.session_state.history[chat_id] = {
        "id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "messages": []
    }

    st.session_state.current_chat_id = chat_id
    st.session_state.messages = []

    save_history(st.session_state.history)


def ensure_current_chat():
    """Make sure there is a chat object for the current conversation."""
    if st.session_state.current_chat_id is None:
        create_chat()

    chat_id = st.session_state.current_chat_id

    if chat_id not in st.session_state.history:
        create_chat()


def sync_current_chat():
    """Copy current messages into persistent history without overwriting custom names."""
    ensure_current_chat()

    chat_id = st.session_state.current_chat_id
    chat = st.session_state.history[chat_id]

    chat["messages"] = st.session_state.messages

    # Only auto-generate a title while the chat still has the default name.
    # Once the user renames it, the custom name is permanent.
    if not chat.get("custom_title", False) and chat.get("title", "New Chat") == "New Chat":
        generated_title = make_chat_title(st.session_state.messages)
        if generated_title != "New Chat":
            chat["title"] = generated_title

    chat["updated_at"] = datetime.now().isoformat(timespec="seconds")
    save_history(st.session_state.history)


def rename_chat(chat_id, new_title):
    """Rename a saved chat and permanently preserve its custom title."""
    if chat_id not in st.session_state.history:
        return

    title = re.sub(r"\s+", " ", str(new_title).strip())
    if not title:
        title = "New Chat"

    chat = st.session_state.history[chat_id]
    chat["title"] = title[:60]
    chat["custom_title"] = True
    chat["updated_at"] = datetime.now().isoformat(timespec="seconds")

    save_history(st.session_state.history)


def load_chat(chat_id):
    """Load a saved chat into the active session."""
    chat = st.session_state.history.get(chat_id)

    if not chat:
        return

    st.session_state.current_chat_id = chat_id
    st.session_state.messages = chat.get("messages", [])


def delete_chat(chat_id):
    """Delete a saved chat."""
    if chat_id in st.session_state.history:
        del st.session_state.history[chat_id]

    if st.session_state.current_chat_id == chat_id:
        st.session_state.current_chat_id = None
        st.session_state.messages = []

    save_history(st.session_state.history)

    if not st.session_state.history:
        create_chat()


# =========================================================
# LOAD HISTORY ON FIRST RUN
# =========================================================

if not st.session_state.history_loaded:
    st.session_state.history = load_history()
    st.session_state.history_loaded = True

    if st.session_state.history:
        # Load most recently updated chat.
        sorted_chats = sorted(
            st.session_state.history.values(),
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )

        latest = sorted_chats[0]

        st.session_state.current_chat_id = latest.get("id")
        st.session_state.messages = latest.get("messages", [])

    else:
        create_chat()


# =========================================================
# OFFLINE WHISPER
# =========================================================

@st.cache_resource(show_spinner=False)
def get_whisper_model(model_size):
    """
    Load Faster-Whisper locally.

    IMPORTANT:
    The first run may need internet to download the Whisper model.
    Once the model is present locally, transcription itself is offline.
    """
    if not FASTER_WHISPER_AVAILABLE:
        return None

    return WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8"
    )


def transcribe_offline(audio_bytes, language):
    """Convert recorded audio to text locally."""
    if not FASTER_WHISPER_AVAILABLE:
        raise RuntimeError(
            "Offline voice package is not installed. "
            "Run: pip install faster-whisper"
        )

    if not audio_bytes:
        raise RuntimeError("The recorded audio is empty.")

    # Faster-Whisper uses PyAV internally for common audio formats.
    # Save the browser recording temporarily.
    temp_audio = os.path.join(
        HISTORY_DIR,
        f"voice_{uuid.uuid4().hex}.webm"
    )

    try:
        with open(temp_audio, "wb") as f:
            f.write(audio_bytes)

        model = get_whisper_model(WHISPER_MODEL_SIZE)

        if model is None:
            raise RuntimeError("Whisper model could not be loaded.")

        segments, info = model.transcribe(
            temp_audio,
            language=language,
            beam_size=5,
            vad_filter=True
        )

        text_parts = []

        for segment in segments:
            text_parts.append(segment.text.strip())

        result = " ".join(
            part for part in text_parts if part
        ).strip()

        if not result:
            raise RuntimeError(
                "I could not detect speech in the recording."
            )

        return result

    finally:
        try:
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
        except Exception:
            pass


# =========================================================
# TEXT-TO-SPEECH (TTS)
# =========================================================

def add_response_actions(text, language="en-IN"):
    """
    Visible Copy + Listen + Stop controls for this exact AI response.
    Browser Web Speech API is used for TTS.
    """
    if not text or not text.strip():
        return

    import json as _json

    js_text = _json.dumps(text.strip(), ensure_ascii=False)
    js_lang = _json.dumps(language)

    # The component itself is deliberately tall and has a visible
    # border so the controls cannot disappear into the chat layout.
    component_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{
                box-sizing: border-box;
            }}
            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background: transparent;
                overflow: hidden;
                font-family: Arial, sans-serif;
            }}
            .tts-box {{
                width: 100%;
                min-height: 54px;
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 6px 0;
            }}
            .label {{
                color: #aeb7c5;
                font-size: 12px;
                font-weight: 700;
                margin-right: 2px;
                white-space: nowrap;
            }}
            button {{
                border: 1px solid rgba(120,160,255,.45);
                border-radius: 9px;
                background: #172033;
                color: #ffffff;
                padding: 8px 13px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 700;
                white-space: nowrap;
            }}
            button:hover {{
                background: #22304a;
                border-color: rgba(120,160,255,.85);
            }}
            button:active {{
                transform: translateY(1px);
            }}
            #status {{
                color: #aeb7c5;
                font-size: 12px;
                margin-left: 2px;
                white-space: nowrap;
            }}
        </style>
    </head>
    <body>
        <div class="tts-box">
            <span class="label">🔊 TTS</span>
            <button id="copyBtn">📋 Copy</button>
            <button id="listenBtn">🔊 Listen</button>
            <button id="stopBtn">⏹ Stop</button>
            <span id="status"></span>
        </div>

        <script>
            const responseText = {js_text};
            const targetLanguage = {js_lang};
            const status = document.getElementById("status");

            function setStatus(message, ms) {{
                status.textContent = message;
                if (ms) {{
                    setTimeout(() => {{
                        status.textContent = "";
                    }}, ms);
                }}
            }}

            async function copyText() {{
                try {{
                    if (navigator.clipboard && window.isSecureContext) {{
                        await navigator.clipboard.writeText(responseText);
                    }} else {{
                        const ta = document.createElement("textarea");
                        ta.value = responseText;
                        ta.style.position = "fixed";
                        ta.style.left = "-10000px";
                        document.body.appendChild(ta);
                        ta.focus();
                        ta.select();
                        document.execCommand("copy");
                        ta.remove();
                    }}
                    setStatus("✅ Copied", 1500);
                }} catch (e) {{
                    setStatus("❌ Copy blocked", 1800);
                }}
            }}

            function chooseVoice(lang) {{
                if (!("speechSynthesis" in window)) return null;

                const voices = window.speechSynthesis.getVoices();
                if (!voices || !voices.length) return null;

                const wanted = String(lang || "").toLowerCase();
                const shortWanted = wanted.split("-")[0];

                return (
                    voices.find(v => String(v.lang || "").toLowerCase() === wanted) ||
                    voices.find(v => String(v.lang || "").toLowerCase().startsWith(shortWanted)) ||
                    voices[0]
                );
            }}

            function speakNow() {{
                if (!("speechSynthesis" in window) ||
                    typeof SpeechSynthesisUtterance === "undefined") {{
                    setStatus("❌ TTS unsupported", 2200);
                    return;
                }}

                window.speechSynthesis.cancel();

                const utterance = new SpeechSynthesisUtterance(responseText);
                utterance.lang = targetLanguage;
                utterance.rate = 0.95;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;

                const voice = chooseVoice(targetLanguage);
                if (voice) utterance.voice = voice;

                utterance.onstart = function() {{
                    setStatus("🔊 Speaking...");
                }};

                utterance.onend = function() {{
                    setStatus("✅ Finished", 1500);
                }};

                utterance.onerror = function(event) {{
                    if (event && event.error === "canceled") return;
                    setStatus("❌ Voice error", 2200);
                }};

                window.speechSynthesis.speak(utterance);
            }}

            function listenNow() {{
                if (!("speechSynthesis" in window)) {{
                    setStatus("❌ TTS unsupported", 2200);
                    return;
                }}

                const voices = window.speechSynthesis.getVoices();

                // Chrome can populate voices asynchronously.
                if (voices && voices.length) {{
                    speakNow();
                    return;
                }}

                const oldHandler = window.speechSynthesis.onvoiceschanged;
                window.speechSynthesis.onvoiceschanged = function() {{
                    window.speechSynthesis.onvoiceschanged = oldHandler || null;
                    speakNow();
                }};

                setTimeout(speakNow, 250);
            }}

            function stopNow() {{
                if ("speechSynthesis" in window) {{
                    window.speechSynthesis.cancel();
                    setStatus("⏹ Stopped", 1300);
                }}
            }}

            document.getElementById("copyBtn").onclick = copyText;
            document.getElementById("listenBtn").onclick = listenNow;
            document.getElementById("stopBtn").onclick = stopNow;
        </script>
    </body>
    </html>
    """

    components.html(component_html, height=62, scrolling=False)


# =========================================================
# GEMINI AI BACKEND — CLOUD ONLY
# =========================================================

GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
]
GEMINI_MODEL = GEMINI_MODELS[0]



def get_gemini_api_key():
    """Read Gemini API key from Streamlit Secrets or environment."""
    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return str(key).strip()
    except Exception:
        pass

    return os.environ.get("GEMINI_API_KEY", "").strip()


@st.cache_resource(show_spinner=False)
def get_gemini_client():
    """Create the Gemini client once and reuse it across Streamlit reruns."""
    api_key = get_gemini_api_key()

    if not api_key:
        return None

    if genai is None:
        return None

    return genai.Client(api_key=api_key)


def gemini_image_response(system_prompt, user_text, image_bytes, image_name):
    """Fast Gemini vision generation with one short retry/fallback."""
    client = get_gemini_client()

    if client is None:
        raise RuntimeError(
            "Gemini is not configured. Check GEMINI_API_KEY in "
            "Streamlit Cloud → Manage app → Settings → Secrets."
        )

    extension = os.path.splitext(image_name or "")[1].lower()
    mime_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(extension, "image/png")

    image_part = genai_types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = (
        system_prompt
        + "\n\nInspect the image carefully and answer the student's request. "
        + "For school questions, solve step by step when useful.\n\n"
        + "Student request: " + user_text
    )

    errors = []

    for index, model_name in enumerate(GEMINI_MODELS):
        attempts = 1 if index else 2

        for attempt in range(attempts):
            try:
                if model_name in {
                    "gemini-3.6-flash",
                    "gemini-3.5-flash-lite",
                    "gemini-3.7-flash",
                    "gemini-3.5-flash",
                    "gemini-3.1-flash-lite",
                }:
                    config = genai_types.GenerateContentConfig(
                        thinking_config=genai_types.ThinkingConfig(
                            thinking_level="minimal"
                        ),
                        max_output_tokens=1200,
                    )
                else:
                    config = genai_types.GenerateContentConfig(
                        thinking_config=genai_types.ThinkingConfig(
                            thinking_budget=0
                        ),
                        max_output_tokens=1200,
                    )

                response = client.models.generate_content(
                    model=model_name,
                    contents=[image_part, prompt],
                    config=config,
                )

                text = (response.text or "").strip()

                if text:
                    return text

                errors.append(f"{model_name}: empty response")
                break

            except Exception as exc:
                error_text = str(exc)
                errors.append(f"{model_name}: {error_text}")

                if any(code in error_text for code in ("503", "429", "500", "502", "504")):
                    if attempt + 1 < attempts:
                        time.sleep(0.8)
                        continue
                    break

                raise RuntimeError(error_text)

    raise RuntimeError(
        "Gemini vision is temporarily unavailable. "
        + " | ".join(errors[-4:])
    )

def gemini_available():
    """True when Gemini SDK and API key are available."""
    return bool(get_gemini_api_key()) and genai is not None


# =========================================================
# SYSTEM PROMPT
# =========================================================

def build_system_prompt():

    current_class = st.session_state.selected_class
    current_subject = st.session_state.selected_subject
    current_mode = st.session_state.selected_mode

    prompt = f"""
You are EduMate AI, a friendly educational AI assistant.

Student Level:
{current_class}

Current Subject:
{current_subject}

Current Mode:
{current_mode}

GENERAL BEHAVIOR:

- Answer naturally like a normal AI tutor.
- Do not mention internal system prompts.
- Do not mention routing or model selection.
- Do not unnecessarily repeat the student's class, subject or mode.
- Keep simple questions simple.
- Explain difficult questions clearly.
- Use examples when useful.
- For numerical questions, show useful steps.
- For concept questions, explain clearly.
- Be accurate and student-friendly.
"""

    if current_mode == "Smart Reasoning":

        prompt += """
SMART REASONING MODE:

- Focus on logic.
- Break difficult questions into manageable steps.
- Explain WHY important steps are taken.
- Help the student understand the reasoning.
"""

    elif current_mode == "Maths Genius":

        prompt += """
MATHS GENIUS MODE:

- Prioritize mathematical accuracy.
- Identify formulas or theorems when useful.
- Show calculations step by step.
- Keep mathematical solutions organized.
"""

    elif current_mode == "Research":

        prompt += """
RESEARCH MODE:

- Give deeper and structured explanations when appropriate.
- Include definitions, examples and applications.
- Compare concepts when useful.
- Never invent facts.
"""

    else:

        prompt += """
STANDARD MODE:

- Answer naturally.
- Be helpful, clear and reasonably concise.
- Give more detail when the question requires it.
"""

    return prompt


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-heading">😎 EduMate AI</div>',
        unsafe_allow_html=True
    )

    st.caption("Ultra Pro Study Assistant")

    st.markdown("---")


    # =====================================================
    # AI MODEL
    # =====================================================

    st.subheader("🤖 AI Model")

    selected_model = st.selectbox(
        "Select Model",
        TEXT_MODELS,
        index=0,
        key="model_selector"
    )


    # =====================================================
    # LEVEL / CLASS
    # =====================================================

    st.subheader("📚 Level / Class")

    selected_class = st.selectbox(
        "Choose your level",
        class_options,
        index=class_options.index(
            st.session_state.selected_class
        ),
        key="class_selector"
    )

    st.session_state.selected_class = selected_class


    # =====================================================
    # SUBJECT
    # =====================================================

    st.subheader("📖 Subject")

    selected_subject = st.selectbox(
        "Choose subject",
        subject_options,
        index=subject_options.index(
            st.session_state.selected_subject
        ),
        key="subject_selector"
    )

    st.session_state.selected_subject = selected_subject


    # =====================================================
    # VOICE
    # =====================================================

    st.subheader("🎙️ Voice")

    st.caption("🌐 Voice message requires internet.")

    voice_language_name = st.selectbox(
        "Voice language",
        list(voice_languages.keys()),
        index=0,
        key="voice_language_selector"
    )

    voice_language = voice_languages[
        voice_language_name
    ]

    if FASTER_WHISPER_AVAILABLE:
        st.caption(
            "🎙️ Offline voice-to-text enabled. "
            "First Whisper model download may require internet."
        )
    else:
        st.warning(
            "Offline voice is not installed. "
            "Run: pip install faster-whisper"
        )


    st.markdown("---")


    # =====================================================
    # SETTINGS
    # =====================================================

    st.subheader("⚙️ Settings")

    max_tokens = st.slider(
        "Max Tokens",
        min_value=100,
        max_value=2000,
        value=512,
        step=50
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.1,
        max_value=1.0,
        value=0.7,
        step=0.1
    )


    # =====================================================
    # CHAT HISTORY — ChatGPT-style
    # =====================================================

    st.markdown("---")
    st.subheader("💾 Chat History")

    if st.button(
        "➕ New Chat",
        use_container_width=True,
        key="new_chat_history"
    ):
        create_chat()
        st.rerun()

    if st.session_state.history:

        sorted_history = sorted(
            st.session_state.history.values(),
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )

        for chat in sorted_history:

            chat_id = chat.get("id")
            title = chat.get("title", "New Chat").strip() or "New Chat"

            is_current = (
                chat_id == st.session_state.current_chat_id
            )

            # One compact row: title on the left, ⋯ on the right.
            row1, row2 = st.columns([0.84, 0.16], gap="small")

            with row1:
                button_text = (
                    f"🟢 {title}"
                    if is_current
                    else f"💬 {title}"
                )

                if st.button(
                    button_text,
                    key=f"load_{chat_id}",
                    use_container_width=True,
                    help=title
                ):
                    load_chat(chat_id)
                    st.session_state.history_menu = None
                    st.rerun()

            with row2:
                if st.button(
                    "⋯",
                    key=f"menu_{chat_id}",
                    help="Rename or delete chat"
                ):
                    if st.session_state.get("history_menu") == chat_id:
                        st.session_state.history_menu = None
                    else:
                        st.session_state.history_menu = chat_id

            # The ⋯ menu opens only for that chat.
            if st.session_state.get("history_menu") == chat_id:

                st.caption("Chat options")

                rename_value = st.text_input(
                    "Rename chat",
                    value=title,
                    max_chars=60,
                    key=f"rename_value_{chat_id}",
                    label_visibility="collapsed",
                    placeholder="Chat name"
                )

                opt1, opt2 = st.columns(2, gap="small")

                with opt1:
                    if st.button(
                        "✏️ Rename",
                        key=f"rename_{chat_id}",
                        use_container_width=True
                    ):
                        rename_chat(chat_id, rename_value)
                        st.session_state.history_menu = None
                        st.rerun()

                with opt2:
                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{chat_id}",
                        use_container_width=True
                    ):
                        delete_chat(chat_id)
                        st.session_state.history_menu = None
                        st.rerun()

    # =====================================================
    # CLEAR CURRENT CHAT
    # =====================================================

    st.markdown("---")

    st.subheader("🗑️ Chat")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []

        # Keep current chat but clear its saved messages.
        ensure_current_chat()

        st.session_state.history[
            st.session_state.current_chat_id
        ]["messages"] = []

        st.session_state.history[
            st.session_state.current_chat_id
        ]["title"] = "New Chat"

        st.session_state.history[
            st.session_state.current_chat_id
        ]["updated_at"] = datetime.now().isoformat(
            timespec="seconds"
        )

        save_history(st.session_state.history)

        st.rerun()


    st.markdown("---")

    st.markdown(
        """
        <div class="small-note">
            Developed by Vaibhav gupta<br>
            EduMate AI Ultra Pro
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="main-title">😎 EduMate AI Ultra Pro</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Your AI study companion — ask questions, solve problems and learn smarter.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SMALL CURRENT STATUS BOX
# =========================================================

st.markdown(
    f"""
    <div class="current-status-box">
        <span class="current-label">Current:</span>
        🎓 {st.session_state.selected_class}
        <span style="color:#666;"> • </span>
        📘 {st.session_state.selected_subject}
        <span style="color:#666;"> • </span>
        🧠 {st.session_state.selected_mode}
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CURRENT MODE INFO
# =========================================================

current_mode = st.session_state.selected_mode

st.markdown(
    f"""
    <div class="mode-info">
        <b>🧠 {current_mode}</b><br>
        <span style="color:#aeb7c5;">
            {mode_descriptions[current_mode]}
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FOUR LEARNING MODE BOXES
# =========================================================

st.subheader("⚡ Choose Your Learning Mode")

mode_col1, mode_col2, mode_col3, mode_col4 = st.columns(4)


with mode_col1:

    if st.button(
        "🧠 Smart Reasoning\n\nLogic • Concepts • Steps",
        use_container_width=True
    ):
        st.session_state.selected_mode = "Smart Reasoning"
        st.rerun()


with mode_col2:

    if st.button(
        "➗ Maths Genius\n\nMath • Formula • Solve",
        use_container_width=True
    ):
        st.session_state.selected_mode = "Maths Genius"
        st.rerun()


with mode_col3:

    if st.button(
        "🔎 Research\n\nDeep • Detailed • Structured",
        use_container_width=True
    ):
        st.session_state.selected_mode = "Research"
        st.rerun()


with mode_col4:

    if st.button(
        "✨ Standard\n\nBalanced AI Study",
        use_container_width=True
    ):
        st.session_state.selected_mode = "Standard"
        st.rerun()


st.markdown("---")


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):

            # Show saved image if this message contains one.
            image_path = message.get("image_path")

            if image_path and os.path.exists(image_path):
                st.image(
                    image_path,
                    caption="Uploaded image",
                    use_container_width=True
                )

            content = message.get("content", "")

            if content:
                st.markdown(content)


    elif message["role"] == "assistant":

        with st.chat_message(
            "assistant",
            avatar="😎"
        ):
            assistant_text = message.get("content", "")
            st.markdown(assistant_text)
            # Buttons are attached to THIS exact response.
            add_response_actions(
                assistant_text,
                tts_languages.get(
                    st.session_state.get(
                        "voice_language_selector",
                        "English (India)"
                    ),
                    "en-IN"
                )
            )


# =========================================================
# INPUT FORM
# =========================================================

with st.form(
    "chat_form",
    clear_on_submit=True
):

    user_input = st.text_input(
        "Your message",
        placeholder="Type your message...",
        label_visibility="collapsed"
    )


    st.markdown("##### 🎙️ Voice / 📷 Image")


    input_col1, input_col2 = st.columns(2)


    # =====================================================
    # VOICE RECORDER
    # =====================================================

    with input_col1:

        voice_file = st.audio_input(
            "🎙️ Record your question",
            sample_rate=16000
        )


    # =====================================================
    # IMAGE UPLOAD
    # =====================================================

    with input_col2:

        image_file = st.file_uploader(
            "📷 Upload image",
            type=["png", "jpg", "jpeg"],
            key="image_uploader"
        )


    st.markdown("")


    submit = st.form_submit_button(
        "📤 Send",
        use_container_width=True
    )


# =========================================================
# PROCESS INPUT
# =========================================================

if submit:

    # -----------------------------------------------------
    # TYPED TEXT
    # -----------------------------------------------------

    typed_text = user_input.strip()

    voice_text = ""


    # -----------------------------------------------------
    # VOICE -> OFFLINE TEXT
    # -----------------------------------------------------

    if voice_file is not None:

        try:

            with st.spinner(
                "🎙️ Converting voice locally..."
            ):

                audio_bytes = voice_file.getvalue()

                voice_text = transcribe_offline(
                    audio_bytes,
                    voice_language
                )


        except Exception as e:

            st.error(
                f"""
                🎙️ Offline voice processing failed.

                Error:
                {str(e)}

                If Faster-Whisper is not installed, run:
                pip install faster-whisper

                The first Whisper model download may require internet.
                After the model is downloaded, transcription is local.
                """
            )

            st.stop()


    # -----------------------------------------------------
    # FINAL MESSAGE
    # -----------------------------------------------------

    if typed_text:

        final_text = typed_text

    elif voice_text:

        final_text = voice_text

    elif image_file is not None:

        final_text = (
            "Analyze this image carefully. "
            "Identify what is shown and explain it clearly "
            "as an educational tutor."
        )

    else:

        st.warning(
            "Please type a message, record your voice, "
            "or upload an image."
        )

        st.stop()


    # -----------------------------------------------------
    # SAVE IMAGE LOCALLY
    # -----------------------------------------------------

    saved_image_path = None

    if image_file is not None:

        try:

            image_bytes_for_save = image_file.getvalue()

            if not image_bytes_for_save:
                raise RuntimeError(
                    "The uploaded image is empty."
                )

            extension = os.path.splitext(
                image_file.name
            )[1].lower()

            if extension not in [".png", ".jpg", ".jpeg"]:
                extension = ".png"

            saved_image_path = os.path.join(
                IMAGES_DIR,
                f"{uuid.uuid4().hex}{extension}"
            )

            with open(
                saved_image_path,
                "wb"
            ) as f:
                f.write(image_bytes_for_save)

        except Exception as e:

            st.error(
                f"Could not save uploaded image: {e}"
            )

            st.stop()


    # -----------------------------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------------------------

    user_message = {
        "role": "user",
        "content": final_text
    }

    if saved_image_path:
        user_message["image_path"] = saved_image_path

    st.session_state.messages.append(
        user_message
    )


    # -----------------------------------------------------
    # GENERATE RESPONSE
    # -----------------------------------------------------

    try:

        if not gemini_available():
            raise RuntimeError(
                "Gemini is not configured. Add GEMINI_API_KEY to "
                "Streamlit Cloud → Manage app → Settings → Secrets, "
                "and make sure google-genai is installed."
            )

        # =================================================
        # IMAGE ANALYSIS REQUEST
        # =================================================

        elif image_file is not None:

            with st.spinner(
                "🖼️ EduMate AI is analyzing the image..."
            ):

                image_bytes = image_file.getvalue()

                if not image_bytes:
                    raise RuntimeError(
                        "The uploaded image is empty."
                    )

                ai_response = gemini_image_response(
                    build_system_prompt(),
                    final_text,
                    image_bytes,
                    image_file.name
                )

        # =================================================
        # NORMAL TEXT / VOICE
        # =================================================

        else:

            with st.spinner(
                "🤔 EduMate AI is thinking..."
            ):

                ai_response = gemini_text_response(
                    build_system_prompt(),
                    st.session_state.messages
                )

        # =================================================
        # VALIDATE RESPONSE
        # =================================================

        ai_response = (ai_response or "").strip()

        if not ai_response:
            raise RuntimeError(
                "Gemini returned an empty response."
            )


        # =================================================
        # SAVE AI RESPONSE
        # =================================================

        # Image-generation requests already save their assistant message
        # together with the generated image path.
        if not (
            image_file is None
            and st.session_state.messages
            and st.session_state.messages[-1].get("generated_image_path")
        ):
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": ai_response
                }
            )

            # =================================================
            # SAVE TO PERMANENT HISTORY
            # =================================================

            sync_current_chat()


    except Exception as e:

        # -------------------------------------------------
        # REMOVE FAILED USER MESSAGE
        # -------------------------------------------------

        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "user"
            and st.session_state.messages[-1].get("content")
            == final_text
        ):

            st.session_state.messages.pop()


        # -------------------------------------------------
        # REMOVE EMPTY SAVED IMAGE IF REQUEST FAILED
        # -------------------------------------------------

        if saved_image_path and os.path.exists(
            saved_image_path
        ):

            try:
                os.remove(saved_image_path)
            except Exception:
                pass


        # -------------------------------------------------
        # IMAGE ERROR
        # -------------------------------------------------

        if image_file is not None:

            st.error(
                f"""
❌ Image analysis failed.

Backend:
Gemini Cloud

Error:
{str(e)}
"""
            )


        # -------------------------------------------------
        # NORMAL ERROR
        # -------------------------------------------------

        else:

            st.error(
                f"""
❌ EduMate AI could not generate a response.

Backend:
Gemini Cloud

Primary model:
{GEMINI_MODEL}

Error:
{str(e)}
"""
            )

            # IMPORTANT:
            # Do not rerun after a failed request. Otherwise Streamlit
            # clears the error immediately and it looks like the message
            # simply disappeared.
            st.stop()


    # Rerun only after a successful response so the new message appears
    # immediately in the chat history.
    st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    f"😎 EduMate AI Ultra Pro • "
    f"{st.session_state.selected_class} • "
    f"{st.session_state.selected_subject} • "
    f"{st.session_state.selected_mode} • "
    f"Developed by Vaibhav Gupta"
)

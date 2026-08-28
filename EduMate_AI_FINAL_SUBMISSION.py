import streamlit as st
import streamlit.components.v1 as components
import ollama
import base64
import io
import json
import os
import requests
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
    "llama3.2",
    "mistral",
    "deepseek-r1:7b",
    "phi3"
]

# Your original vision model.
# If you have another Ollama vision model installed, change this.
VISION_MODEL = "llava:7b"

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

# 1. Setup paths and data (Keep this outside your loop, at the start of your function)
HISTORY_FILE = "chat_history.json"
MODEL_NAME = "llama3"
OLLAMA_URL = "http://localhost:11434/api/chat"

# Load history if file exists
chat_history = []
if os.path.exists(HISTORY_FILE):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            chat_history = json.load(f)
    except json.JSONDecodeError:
        chat_history = []

# Show previous history to the user
for chat in chat_history:
    role_label = "User" if chat["role"] == "user" else "AI"
    print(f"{role_label}: {chat['content']}")


# 2. Inside your input logic / button click event
# Replace 'user_input_variable' with your actual input variable name
user_input_variable = "Hello, how are you?"

if user_input_variable.strip():
    # Append user message to history
    chat_history.append({"role": "user", "content": user_input_variable})

    # Prepare payload and send request
    payload = {"model": MODEL_NAME, "messages": chat_history, "stream": False}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        ai_reply = response.json()["message"]["content"]

        # Print/Display the AI reply
        print(f"AI: {ai_reply}")

        # Append AI reply to history and save to file immediately
        chat_history.append({"role": "assistant", "content": ai_reply})
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=4, ensure_ascii=False)

    except requests.exceptions.ConnectionError:
        print("Error: Ollama server is not running.")
    except Exception as e:
        print(f"Error: {e}")


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
    """Copy current messages into persistent history."""
    ensure_current_chat()

    chat_id = st.session_state.current_chat_id

    chat = st.session_state.history[chat_id]
    chat["messages"] = st.session_state.messages
    chat["title"] = make_chat_title(st.session_state.messages)
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
# OLLAMA HELPERS


# =========================================================

def get_installed_ollama_models():
    """Return installed Ollama model names."""
    try:
        result = ollama.list()
        models = result.get("models", [])

        names = []

        for model in models:
            name = model.get("name")

            if name:
                names.append(name)

        return names

    except Exception:
        return []


def find_vision_model():
    """
    Pick a vision model from the installed Ollama models.
    Prefer the user's original llava:7b.
    """
    installed = get_installed_ollama_models()

    if VISION_MODEL in installed:
        return VISION_MODEL

    vision_candidates = [
        "llava:7b",
        "llava",
        "llama3.2-vision:11b",
        "llama3.2-vision:latest",
        "llama3.2-vision"
    ]

    for candidate in vision_candidates:
        if candidate in installed:
            return candidate

    # Also allow tag variations such as llava:13b.
    for name in installed:
        low = name.lower()

        if "llava" in low or "vision" in low:
            return name

    return None


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
            "🎙️ Offline voice message enabled. "
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
    # CHAT HISTORY
    # =====================================================

    st.markdown("---")

    st.subheader("💾 Chat History")

    if st.button(
        "➕ New Chat",
        use_container_width=True
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
            title = chat.get("title", "New Chat")

            if not title.strip():
                title = "New Chat"

            is_current = (
                chat_id == st.session_state.current_chat_id
            )

            button_text = (
                f"🟢 {title}"
                if is_current
                else f"💬 {title}"
            )

            if st.button(
                button_text,
                key=f"load_{chat_id}",
                use_container_width=True
            ):
                load_chat(chat_id)
                st.rerun()

            if is_current:

                if st.button(
                    "🗑️ Delete This Chat",
                    key=f"delete_{chat_id}",
                    use_container_width=True
                ):
                    delete_chat(chat_id)
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

        # =================================================
        # IMAGE REQUEST
        # =================================================

        if image_file is not None:

            with st.spinner(
                "🖼️ EduMate AI is analyzing the image..."
            ):

                vision_model = find_vision_model()

                if not vision_model:

                    raise RuntimeError(
                        "No Ollama vision model was found. "
                        "Install one, for example: "
                        "ollama pull llava:7b"
                    )

                image_bytes = image_file.getvalue()

                if not image_bytes:
                    raise RuntimeError(
                        "The uploaded image is empty."
                    )

                # Ollama accepts image bytes directly.
                # This avoids unnecessary base64 conversion.
                vision_messages = [
                    {
                        "role": "system",
                        "content": build_system_prompt()
                        + """

VISION INSTRUCTIONS:

- Carefully inspect the entire image.
- If the image contains a school question, solve it.
- If it contains a diagram, explain the diagram.
- If it contains text, read the relevant text.
- If it contains a mathematical problem, show the solution step by step.
- Do not say that you cannot see the image when the image is available.
- Answer the student's actual question first.
"""
                    },
                    {
                        "role": "user",
                        "content": final_text,
                        "images": [
                            image_bytes
                        ]
                    }
                ]

                response = ollama.chat(
                    model=vision_model,
                    messages=vision_messages,
                    options={
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                )


        # =================================================
        # NORMAL TEXT / VOICE
        # =================================================

        else:

            with st.spinner(
                "🤔 EduMate AI is thinking..."
            ):

                normal_messages = [
                    {
                        "role": "system",
                        "content": build_system_prompt()
                    }
                ] + st.session_state.messages

                response = ollama.chat(
                    model=selected_model,
                    messages=normal_messages,
                    options={
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                )


        # =================================================
        # EXTRACT RESPONSE
        # =================================================

        ai_response = (
            response
            .get("message", {})
            .get("content", "")
            .strip()
        )


        if not ai_response:

            raise RuntimeError(
                "Ollama returned an empty response."
            )


        # =================================================
        # SAVE AI RESPONSE
        # =================================================

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

Vision model:
{find_vision_model() or VISION_MODEL}

Error:
{str(e)}

Make sure Ollama is running and a vision model is installed.

Example:
ollama pull llava:7b
"""
            )


        # -------------------------------------------------
        # NORMAL ERROR
        # -------------------------------------------------

        else:

            st.error(
                f"""
❌ EduMate AI could not generate a response.

Model:
{selected_model}

Error:
{str(e)}
"""
            )


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

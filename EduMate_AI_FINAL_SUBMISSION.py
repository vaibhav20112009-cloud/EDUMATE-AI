import streamlit as st
import ollama
import base64
import speech_recognition as sr
import io


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

# Vision model used for image questions
VISION_MODEL = "llava:7b"


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

section[data-testid="stSidebar"] {
    min-width: 280px;
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

    voice_language_name = st.selectbox(
        "Voice language",
        list(voice_languages.keys()),
        index=0,
        key="voice_language_selector"
    )

    voice_language = voice_languages[
        voice_language_name
    ]

    st.caption(
        "Voice-to-text requires internet."
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
    # CLEAR CHAT
    # =====================================================

    st.markdown("---")

    st.subheader("🗑️ Chat")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
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
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.markdown(
                message["content"]
            )

    elif message["role"] == "assistant":

        with st.chat_message(
            "assistant",
            avatar="😎"
        ):
            st.markdown(
                message["content"]
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
            type=["png", "jpg", "jpeg"]
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
    # VOICE -> TEXT
    # -----------------------------------------------------

    if voice_file is not None:

        try:

            with st.spinner(
                "🎙️ Converting voice to text..."
            ):

                recognizer = sr.Recognizer()

                audio_bytes = voice_file.getvalue()

                if not audio_bytes:
                    raise RuntimeError(
                        "The recorded audio is empty."
                    )

                audio_stream = io.BytesIO(
                    audio_bytes
                )

                with sr.AudioFile(
                    audio_stream
                ) as source:

                    recorded_audio = recognizer.record(
                        source
                    )

                voice_text = recognizer.recognize_google(
                    recorded_audio,
                    language=voice_language
                )


        except sr.UnknownValueError:

            st.error(
                "🎙️ I couldn't understand the recording. "
                "Please speak clearly and try again."
            )

            st.stop()


        except sr.RequestError:

            st.error(
                "🎙️ Voice-to-text service could not be "
                "reached. Check your internet connection."
            )

            st.stop()


        except Exception as e:

            st.error(
                f"🎙️ Voice processing error: {str(e)}"
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
            "Please analyze this image and explain "
            "what is shown in it."
        )

    else:

        st.warning(
            "Please type a message, record your voice, "
            "or upload an image."
        )

        st.stop()


    # -----------------------------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": final_text
        }
    )


    try:

        # =================================================
        # IMAGE REQUEST
        # =================================================

        if image_file is not None:

            with st.spinner(
                "🖼️ Analyzing image..."
            ):

                image_bytes = image_file.read()

                if not image_bytes:

                    raise RuntimeError(
                        "The uploaded image is empty."
                    )

                image_base64 = base64.b64encode(
                    image_bytes
                ).decode("utf-8")


                # Only current image + question
                # are sent to vision model.
                vision_messages = [

                    {
                        "role": "system",
                        "content": build_system_prompt()
                    },

                    {
                        "role": "user",
                        "content": final_text,
                        "images": [
                            image_base64
                        ]
                    }

                ]


                response = ollama.chat(
                    model=VISION_MODEL,
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


    except Exception as e:

        # -------------------------------------------------
        # REMOVE FAILED USER MESSAGE
        # -------------------------------------------------

        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "user"
            and st.session_state.messages[-1]["content"] == final_text
        ):

            st.session_state.messages.pop()


        # -------------------------------------------------
        # IMAGE ERROR
        # -------------------------------------------------

        if image_file is not None:

            st.error(
                f"""
❌ Image analysis failed.

Vision model:
{VISION_MODEL}

Error:
{str(e)}

Check that Ollama is running and `llava:7b`
is available in `ollama list`.
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

import streamlit as st
import re

# ============================================================
# 🤖 EDUMATE AI — CLEAN OFFLINE VERSION
# ============================================================

st.set_page_config(
    page_title="EduMate AI Ultra",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 🎨 UI
# ============================================================

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top right, #090D16, #020408);
    color: #F3F4F6;
    font-family: sans-serif;
}
.main-title {
    font-size: 46px;
    font-weight: 900;
    background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 2px;
}
.sub-title {
    font-size: 15px;
    color: #9CA3AF;
    text-align: center;
    margin-bottom: 30px;
}
[data-testid="stSidebar"] {
    background-color: rgba(10,15,30,0.97);
    border-right: 1px solid #00F2FE40;
}
.stChatMessage {
    border-radius: 20px !important;
    padding: 18px 22px !important;
    margin-bottom: 15px !important;
}
.card {
    background: linear-gradient(145deg, #0B1220, #080D17);
    border: 1px solid #00F2FE30;
    border-radius: 18px;
    padding: 18px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "student_class" not in st.session_state:
    st.session_state.student_class = "Class 9"

# ============================================================
# 📚 CLASS 9–12 IMPORTANT CHAPTERS
# ============================================================

CLASS_CHAPTERS = {
    "Class 9": {
        "Maths": [
            "Number Systems", "Polynomials", "Coordinate Geometry",
            "Linear Equations in Two Variables", "Lines and Angles",
            "Triangles", "Quadrilaterals", "Circles",
            "Heron's Formula", "Surface Areas and Volumes",
            "Statistics", "Probability"
        ],
        "Science": [
            "Matter in Our Surroundings", "Is Matter Around Us Pure",
            "Atoms and Molecules", "Structure of the Atom",
            "Fundamental Unit of Life", "Tissues", "Motion",
            "Force and Laws of Motion", "Gravitation",
            "Work and Energy", "Sound", "Improvement in Food Resources"
        ]
    },

    "Class 10": {
        "Maths": [
            "Real Numbers", "Polynomials",
            "Pair of Linear Equations in Two Variables",
            "Quadratic Equations", "Arithmetic Progressions",
            "Triangles", "Coordinate Geometry",
            "Introduction to Trigonometry",
            "Applications of Trigonometry", "Circles",
            "Areas Related to Circles", "Surface Areas and Volumes",
            "Statistics", "Probability"
        ],
        "Science": [
            "Chemical Reactions and Equations",
            "Acids Bases and Salts", "Metals and Non-metals",
            "Carbon and Its Compounds", "Life Processes",
            "Control and Coordination", "How Do Organisms Reproduce",
            "Heredity", "Light", "Human Eye and Colourful World",
            "Electricity", "Magnetic Effects of Electric Current",
            "Our Environment"
        ]
    },

    "Class 11": {
        "Maths": [
            "Sets", "Relations and Functions", "Trigonometric Functions",
            "Principle of Mathematical Induction",
            "Complex Numbers and Quadratic Equations",
            "Linear Inequalities", "Permutations and Combinations",
            "Binomial Theorem", "Sequences and Series",
            "Straight Lines", "Conic Sections",
            "Introduction to Three Dimensional Geometry",
            "Limits and Derivatives", "Statistics", "Probability"
        ],
        "Physics": [
            "Units and Measurements", "Motion in a Straight Line",
            "Motion in a Plane", "Laws of Motion", "Work Energy and Power",
            "System of Particles and Rotational Motion", "Gravitation",
            "Mechanical Properties of Solids", "Mechanical Properties of Fluids",
            "Thermal Properties of Matter", "Thermodynamics",
            "Kinetic Theory", "Oscillations", "Waves"
        ],
        "Chemistry": [
            "Some Basic Concepts of Chemistry", "Structure of Atom",
            "Classification of Elements and Periodicity",
            "Chemical Bonding", "Thermodynamics", "Equilibrium",
            "Redox Reactions", "Organic Chemistry Basics", "Hydrocarbons"
        ],
        "Biology": [
            "The Living World", "Biological Classification", "Plant Kingdom",
            "Animal Kingdom", "Cell", "Biomolecules", "Cell Cycle",
            "Photosynthesis", "Respiration", "Human Physiology"
        ]
    },

    "Class 12": {
        "Maths": [
            "Relations and Functions", "Inverse Trigonometric Functions",
            "Matrices", "Determinants", "Continuity and Differentiability",
            "Applications of Derivatives", "Integrals",
            "Applications of Integrals", "Differential Equations",
            "Vector Algebra", "Three Dimensional Geometry",
            "Linear Programming", "Probability"
        ],
        "Physics": [
            "Electric Charges and Fields",
            "Electrostatic Potential and Capacitance",
            "Current Electricity", "Moving Charges and Magnetism",
            "Magnetism and Matter", "Electromagnetic Induction",
            "Alternating Current", "Electromagnetic Waves",
            "Ray Optics", "Wave Optics", "Dual Nature of Radiation",
            "Atoms", "Nuclei", "Semiconductor Electronics"
        ],
        "Chemistry": [
            "Solutions", "Electrochemistry", "Chemical Kinetics",
            "d and f Block Elements", "Coordination Compounds",
            "Haloalkanes and Haloarenes", "Alcohols Phenols and Ethers",
            "Aldehydes Ketones and Carboxylic Acids", "Amines",
            "Biomolecules"
        ],
        "Biology": [
            "Reproduction", "Genetics and Evolution",
            "Human Health and Disease", "Biotechnology",
            "Ecology", "Environment"
        ]
    }
}

# ============================================================
# 🤖 ROBOTICS
# ============================================================

ROBOTICS_TEACHERS = [
    "Mr. Shahsank Shekhar Mishra",
    "Mrs. Niyati Tyagi",
    "Mr. Chirag"
]

ROBOTICS_STUDY = """
# 🚀 Best Way to Study Robotics

## ⭐ Best Learning Way / Source
**Kalpana Vimaan**

## 1️⃣ Electronics Basics
- Voltage
- Current
- Resistance
- Ohm's Law
- LED
- Resistor
- Breadboard
- Battery

## 2️⃣ Programming
- Variables
- Data Types
- If / Else
- Loops
- Functions
- Arduino C/C++
- Python

## 3️⃣ Sensors
- IR Sensor
- Ultrasonic Sensor
- LDR
- Temperature Sensor
- Gyroscope
- Accelerometer
- Encoder

## 4️⃣ Motors
- DC Motor
- Servo Motor
- Stepper Motor

## 5️⃣ Arduino
Start with:
- LED Blinking
- Traffic Light
- Push Button
- LDR
- Ultrasonic Sensor
- Servo Motor

Then build:
- Line Following Robot
- Obstacle Avoiding Robot

## 6️⃣ Raspberry Pi
After Arduino basics:
- Linux
- Python
- GPIO
- Camera
- Computer Vision
- Automation
- AI/ML

## 🧠 Golden Rule
**LEARN → BUILD → DEBUG → IMPROVE**

Robotics sirf theory padhne se nahi, projects bana kar seekhi jaati hai.
"""

ROBOTICS = {
    "robotics": """
# 🤖 What is Robotics?

Robotics combines mechanical engineering, electronics,
programming, sensors, actuators and control systems.

Basic flow:

**SENSOR → CONTROLLER → DECISION → ACTUATOR**
""",

    "arduino uno": """
# 🔌 Arduino UNO

Arduino UNO is a microcontroller development board based on
the ATmega328P.

Important concepts:
- Digital I/O
- Analog input
- PWM
- USB
- Power
- Serial communication

Common projects:
- LED
- Traffic light
- Ultrasonic sensor
- Servo
- Line follower
- Obstacle avoiding robot

Basic structure:

```cpp
void setup() {
}

void loop() {
}
```
""",

    "arduino nano": """
# 🔌 Arduino Nano

Arduino Nano is a compact Arduino microcontroller board.

Useful for:
- Small robots
- Compact electronics
- Sensor projects
- Embedded projects

UNO is larger and beginner-friendly; Nano is compact and
useful where board space is limited.
""",

    "raspberry pi": """
# 🍓 Raspberry Pi

Raspberry Pi is a small single-board computer.

Uses:
- Python
- Linux
- GPIO
- Robotics
- Camera
- Computer Vision
- IoT
- Automation
- AI/ML

**Arduino = Microcontroller**

**Raspberry Pi = Single-board computer**
""",

    "sensors": """
# 👁️ Robotics Sensors

**Ultrasonic:** distance measurement.

**IR:** object/reflection detection.

**LDR:** light intensity sensing.

**Gyroscope:** angular motion.

**Accelerometer:** acceleration.

**Encoder:** position/speed feedback.
""",

    "motors": """
# ⚙️ Robotics Motors

**DC Motor:** continuous rotation.

**Servo Motor:** controlled angular position.

**Stepper Motor:** moves in discrete steps for precise positioning.
"""
}

# ============================================================
# 📐 MATH SPECIAL TOPICS
# ============================================================

MATH_KNOWLEDGE = {
    "sets": """
# 📦 SETS

A set is a well-defined collection of objects.

Example:
A = {1, 2, 3, 4}

### Important Concepts
- Empty Set: ∅
- Subset: A ⊆ B
- Union: A ∪ B
- Intersection: A ∩ B
- Difference: A − B
- Complement: A'

### Important Formula
n(A ∪ B) = n(A) + n(B) − n(A ∩ B)
""",

    "relations": """
# 🔗 RELATIONS & FUNCTIONS

A relation from A to B is a subset of A × B.

### Cartesian Product
If A = {1,2} and B = {3,4}:

A × B = {(1,3),(1,4),(2,3),(2,4)}

### Domain
Set of first elements.

### Range
Set of actual second elements.

### Function
A function f : A → B assigns exactly one output to every
input in A.

Types:
- One-One
- Many-One
- Onto
- Into
- Bijective
""",

    "trigonometry": """
# 📐 TRIGONOMETRY

For a right-angled triangle:

sin θ = Perpendicular / Hypotenuse

cos θ = Base / Hypotenuse

tan θ = Perpendicular / Base

### Reciprocal Ratios
cosec θ = 1/sin θ
sec θ = 1/cos θ
cot θ = 1/tan θ

### Identities
sin²θ + cos²θ = 1

1 + tan²θ = sec²θ

1 + cot²θ = cosec²θ

### Standard Values

θ:       0°    30°    45°    60°    90°

sin:     0     1/2    1/√2   √3/2   1

cos:     1     √3/2   1/√2   1/2    0

tan:     0     1/√3   1      √3     Undefined
""",

    "algebra": """
# ➗ ALGEBRA

Important topics:
- Algebraic expressions
- Polynomials
- Identities
- Linear equations
- Quadratic equations
- Inequalities
- Sequences and series
- Functions
- Complex numbers

### Important Identities

(a+b)² = a² + 2ab + b²

(a-b)² = a² - 2ab + b²

a²-b² = (a-b)(a+b)

(a+b)³ = a³ + 3a²b + 3ab² + b³

(a-b)³ = a³ - 3a²b + 3ab² - b³

a³+b³ = (a+b)(a²-ab+b²)

a³-b³ = (a-b)(a²+ab+b²)

### Quadratic Equation

ax² + bx + c = 0

x = (-b ± √(b² - 4ac)) / 2a

Discriminant:
D = b² - 4ac
"""
}

# ============================================================
# 🧹 NORMALIZER
# ============================================================

def normalize(text):
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)

# ============================================================
# 👨‍🏫 TEACHERS
# ============================================================

def teacher_answer():
    return """
# 👨‍🏫 Your Robotics Teachers

### 1. Mr. Shahsank Shekhar Mishra

### 2. Mrs. Niyati Tyagi

### 3. Mr. Chirag
"""

# ============================================================
# 🚀 ROBOTICS STUDY DETECTOR
# ============================================================

def is_robotics_study_question(txt):

    robotics_words = [
        "robotics",
        "robotic",
        "robot"
    ]

    study_words = [
        "study",
        "learn",
        "learning",
        "padh",
        "padhu",
        "padhna",
        "padhai",
        "seekh",
        "seekhu",
        "seekhna",
        "best way",
        "best method",
        "roadmap",
        "how to",
        "kaise"
    ]

    return (
        any(x in txt for x in robotics_words)
        and any(x in txt for x in study_words)
    )

# ============================================================
# 📚 CHAPTERS
# ============================================================

def chapters_answer(student_class, subject=None):

    data = CLASS_CHAPTERS.get(student_class, {})

    if subject and subject in data:

        answer = f"# 📚 {student_class} — {subject}\n\n"

        for i, chapter in enumerate(data[subject], 1):
            answer += f"**{i}. {chapter}**\n\n"

        return answer

    answer = f"# 📚 {student_class} Important Chapters\n\n"

    for subject_name, chapters in data.items():

        answer += f"## {subject_name}\n\n"

        for chapter in chapters:
            answer += f"- {chapter}\n"

        answer += "\n"

    return answer

# ============================================================
# 🧮 CALCULATOR
# ============================================================

def calculate_expression(text):

    text = text.replace("×", "*").replace("÷", "/")

    expressions = re.findall(
        r"[-+*/().\d\s]+",
        text
    )

    if not expressions:
        return None

    expression = max(expressions, key=len).strip()

    if not re.search(r"\d", expression):
        return None

    if not re.fullmatch(
        r"[0-9+\-*/().\s]+",
        expression
    ):
        return None

    try:
        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return f"🧮 **Answer:** `{result}`"

    except Exception:
        return None

# ============================================================
# 🧠 MAIN ANSWER ENGINE
# ============================================================

def get_answer(user_text, student_class):

    txt = normalize(user_text)

    # BEST WAY TO STUDY ROBOTICS — EXACT ANSWER
    if (
        "robotics" in txt
        and (
            "best way" in txt
            or "best method" in txt
            or "how to study" in txt
            or "kaise padhu" in txt
            or "kaise padhe" in txt
            or "kaise padhna" in txt
            or "padhne ka best" in txt
        )
    ):
        return "Best way to study Robotics is obviously by Kalpana Vimaan."

    # ========================================================
    # 🚀 1. ROBOTICS STUDY — FIRST PRIORITY
    # ========================================================

    if is_robotics_study_question(txt):

        return ROBOTICS_STUDY

    # Exact/common robotics-study phrases
    robotics_study_phrases = [
        "best way to study robotics",
        "best way to learn robotics",
        "how to study robotics",
        "how to learn robotics",
        "robotics kaise padhu",
        "robotics kaise padhe",
        "robotics kaise padhna hai",
        "robotics kaise seekhu",
        "robotics kaise seekhe",
        "robotics padhne ka best way",
        "robotics padhne ka best tarika",
        "robotics seekhne ka best way",
        "robotics study roadmap",
        "robotics roadmap",
        "robotics ki padhai kaise karu",
        "robotics ki padhai kaise kare"
    ]

    if any(
        phrase in txt
        for phrase in robotics_study_phrases
    ):
        return ROBOTICS_STUDY

    # ========================================================
    # 👨‍🏫 2. ROBOTICS TEACHERS — SECOND PRIORITY
    # ========================================================

    teacher_words = [
        "teacher",
        "teachers",
        "sir",
        "bhaiya",
        "didi",
        "naam",
        "name",
        "kaun",
        "kon"
    ]

    if (
        "robotics" in txt
        and any(x in txt for x in teacher_words)
    ):
        return teacher_answer()

    teacher_phrases = [
        "mere robotics teacher",
        "mere robotics teachers",
        "my robotics teacher",
        "my robotics teachers",
        "name of my robotics teacher",
        "name of my robotics teachers",
        "names of my robotics teachers",
        "robotics teacher ka naam",
        "robotics teachers ka naam",
        "robotics teacher ke naam",
        "robotics teachers ke naam",
        "robotics ke teacher",
        "robotics ke teachers",
        "robotics ke sir"
    ]

    if any(
        phrase in txt
        for phrase in teacher_phrases
    ):
        return teacher_answer()

    # Individual teacher names
    if (
        "shahsank" in txt
        or "shashank" in txt
    ):
        return """
# 👨‍🏫 Mr. Shahsank Shekhar Mishra

Your Robotics Teacher.
"""

    if "niyati" in txt:
        return """
# 👩‍🏫 Mrs. Niyati Tyagi

Your Robotics Teacher.
"""

    if "chirag" in txt:
        return """
# 👨‍🏫 Mr. Chirag

Your Robotics Teacher.
"""

    # ========================================================
    # 👤 3. IDENTITY
    # ========================================================

    if any(
        x in txt
        for x in [
            "who are you",
            "tum kon ho",
            "tum kaun ho",
            "aap kon ho",
            "what is your name",
            "your name",
            "naam kya hai"
        ]
    ):

        return """
# 🤖 I am EduMate AI

Mujhe **Vaibhav Gupta** ne banaya hai.

Main help kar sakta hoon:

📚 Class 9–12

➗ Maths

🔬 Science

🤖 Robotics

🔌 Arduino UNO

🔌 Arduino Nano

🍓 Raspberry Pi

📦 Sets

🔗 Relations & Functions

📐 Trigonometry

➗ Algebra
"""

    # ========================================================
    # 📦 4. SETS
    # ========================================================

    if (
        txt in ["set", "sets"]
        or "sets kya hai" in txt
        or "set kya hai" in txt
        or "what is set" in txt
        or "set theory" in txt
        or "sets samjhao" in txt
        or "sets explain" in txt
    ):
        return MATH_KNOWLEDGE["sets"]

    # ========================================================
    # 🔗 5. RELATIONS & FUNCTIONS
    # ========================================================

    if (
        "relations and functions" in txt
        or "relation and function" in txt
        or "relation kya hai" in txt
        or "function kya hai" in txt
        or "what is relation" in txt
        or "what is function" in txt
        or "relations functions" in txt
    ):
        return MATH_KNOWLEDGE["relations"]

    # ========================================================
    # 📐 6. TRIGONOMETRY
    # ========================================================

    if (
        "trigonometry" in txt
        or "trigonometric" in txt
        or "trigo" in txt
        or "sin theta" in txt
        or "cos theta" in txt
        or "tan theta" in txt
    ):
        return MATH_KNOWLEDGE["trigonometry"]

    # ========================================================
    # ➗ 7. ALGEBRA
    # ========================================================

    if (
        txt == "algebra"
        or "what is algebra" in txt
        or "algebra kya hai" in txt
        or "algebra explain" in txt
        or "algebra samjhao" in txt
        or "algebraic identity" in txt
    ):
        return MATH_KNOWLEDGE["algebra"]

    # ========================================================
    # 🔌 8. ARDUINO UNO
    # ========================================================

    if "arduino uno" in txt:
        return ROBOTICS["arduino uno"]

    # ========================================================
    # 🔌 9. ARDUINO NANO
    # ========================================================

    if "arduino nano" in txt:
        return ROBOTICS["arduino nano"]

    # ========================================================
    # 🍓 10. RASPBERRY PI
    # ========================================================

    if "raspberry pi" in txt or "raspberry" in txt:
        return ROBOTICS["raspberry pi"]

    # ========================================================
    # 👁️ 11. SENSORS
    # ========================================================

    if (
        "robotics sensor" in txt
        or "robotics sensors" in txt
        or "sensor in robotics" in txt
        or "sensors in robotics" in txt
    ):
        return ROBOTICS["sensors"]

    # ========================================================
    # ⚙️ 12. MOTORS
    # ========================================================

    if (
        "dc motor" in txt
        or "servo motor" in txt
        or "stepper motor" in txt
        or "motors in robotics" in txt
    ):
        return ROBOTICS["motors"]

    # ========================================================
    # 🤖 13. GENERAL ROBOTICS
    # ========================================================

    if (
        txt == "robotics"
        or "what is robotics" in txt
        or "robotics kya hai" in txt
        or "robotics basics" in txt
        or "robotics explain" in txt
    ):
        return ROBOTICS["robotics"]

    # ========================================================
    # 📚 14. CLASS DETECTION
    # ========================================================

    detected_class = student_class

    if "class 9" in txt or "9th" in txt:
        detected_class = "Class 9"

    elif "class 10" in txt or "10th" in txt:
        detected_class = "Class 10"

    elif "class 11" in txt or "11th" in txt:
        detected_class = "Class 11"

    elif "class 12" in txt or "12th" in txt:
        detected_class = "Class 12"

    # ========================================================
    # 📖 15. CHAPTERS
    # ========================================================

    if (
        "chapter" in txt
        or "chapters" in txt
        or "syllabus" in txt
    ):

        subject = None

        if "math" in txt:
            subject = "Maths"

        elif "physics" in txt:
            subject = "Physics"

        elif "chemistry" in txt:
            subject = "Chemistry"

        elif "biology" in txt:
            subject = "Biology"

        elif "science" in txt:
            subject = "Science"

        return chapters_answer(
            detected_class,
            subject
        )

    # ========================================================
    # 👋 16. GREETING
    # ========================================================

    if txt in [
        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "namaste"
    ]:
        return """
# 👋 Hey!

Main **EduMate AI** hoon 🤖

Tu mujhse Maths, Science aur Robotics ke questions pooch sakta hai.
"""

    # ========================================================
    # 🧮 17. CALCULATOR
    # ========================================================

    if any(
        x in txt
        for x in ["+", "-", "*", "/", "×", "÷"]
    ):

        answer = calculate_expression(txt)

        if answer:
            return answer

    # ========================================================
    # ❓ DEFAULT
    # ========================================================

    return """
🤔 Is question ka exact answer meri current offline knowledge base
mein nahi mila.

Try asking:

• Mere robotics teachers kaun hain?
• Robotics teacher ke naam batao
• Best way to study robotics?
• Robotics kaise padhu?
• Kalpana Vimaan
• Sets kya hai?
• Relations and Functions samjhao
• Trigonometry samjhao
• Algebra kya hai?
• Arduino UNO kya hai?
• Arduino Nano kya hai?
• Raspberry Pi kya hai?
• Class 11 Maths chapters
"""

# ============================================================
# 🛠️ SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🤖 EduMate Control Panel")

    classes = [
        "Class 9",
        "Class 10",
        "Class 11",
        "Class 12"
    ]

    st.session_state.student_class = st.selectbox(
        "🎓 Select Class",
        classes,
        index=classes.index(
            st.session_state.student_class
        )
    )

    st.markdown("---")

    st.markdown("### ⚡ Quick Topics")

    quick_topics = [
        ("📦 Sets", "Sets"),
        ("🔗 Relations & Functions", "Relations and Functions"),
        ("📐 Trigonometry", "Trigonometry"),
        ("➗ Algebra", "Algebra"),
        ("🤖 Robotics", "Robotics"),
        ("🔌 Arduino UNO", "Arduino UNO"),
        ("🔌 Arduino Nano", "Arduino Nano"),
        ("🍓 Raspberry Pi", "Raspberry Pi"),
        ("👨‍🏫 Robotics Teachers", "My Robotics Teachers"),
        ("🚀 Robotics Study Method", "Best way to study robotics")
    ]

    for button_name, question in quick_topics:

        if st.button(
            button_name,
            use_container_width=True
        ):

            st.session_state.messages.append({
                "role": "user",
                "content": question
            })

            st.session_state.messages.append({
                "role": "assistant",
                "content": get_answer(
                    question,
                    st.session_state.student_class
                )
            })

            st.rerun()

    st.markdown("---")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()

# ============================================================
# 🏠 DASHBOARD
# ============================================================

st.markdown(
    '<div class="main-title">🤖 EduMate AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Offline Study Assistant • Class 9–12 • Maths • Science • Robotics'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    f"""
<div class="card">

<h3>🎓 Current Class: {st.session_state.student_class}</h3>

Ask me things like:

<br><br>

<b>"Mere robotics teachers kaun hain?"</b><br>
<b>"Best way to study robotics?"</b><br>
<b>"Robotics kaise padhu?"</b><br>
<b>"Kalpana Vimaan"</b><br>
<b>"Sets kya hai?"</b><br>
<b>"Relations and Functions samjhao"</b><br>
<b>"Trigonometry samjhao"</b><br>
<b>"Arduino UNO kya hai?"</b><br>
<b>"Raspberry Pi kya hai?"</b>

</div>
""",
    unsafe_allow_html=True
)

# ============================================================
# 💬 CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

# ============================================================
# 💬 CHAT INPUT
# ============================================================

prompt = st.chat_input("💬 Ask EduMate AI...")

if prompt:

    clean_prompt = prompt.lower().strip()

    # Absolute direct answer for the requested robotics question.
    if (
        "robotics" in clean_prompt
        and (
            "best way" in clean_prompt
            or "best method" in clean_prompt
            or "how to study" in clean_prompt
            or "kaise padhu" in clean_prompt
            or "kaise padhe" in clean_prompt
            or "kaise padhna" in clean_prompt
            or "padhne ka best" in clean_prompt
        )
    ):
        answer = "Best way to study Robotics is obviously by Kalpana Vimaan."
    else:
        answer = get_answer(
            prompt,
            st.session_state.student_class
        )

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
<div style="text-align:center;color:#64748B;font-size:12px;">
🤖 EduMate AI — Study Smart • Learn Science • Build Robots
</div>
""",
    unsafe_allow_html=True
)

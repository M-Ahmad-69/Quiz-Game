# # To Downlaod and Run App on your System(Follow Steps)
# 1. navigate to project folder / open in vs code
# 2. uv venv
# 3. .venv\Scripts\activate
# 4. (uv sync) uv add streamlit google-genai python-dotenv
# 5. create .env and add your key (GEMINI_API_KEY=)
# 6. streamlit run main.py


import streamlit as st
from google import genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="AI QUIZ Game App", page_icon="🎯", layout="centered")

# Initialize session state variables
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'setup'  # setup, loading, playing, results
if 'categories' not in st.session_state:
    st.session_state.categories = []
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = 'medium'
if 'num_questions' not in st.session_state:
    st.session_state.num_questions = 3
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'selected_answer' not in st.session_state:
    st.session_state.selected_answer = None
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'client' not in st.session_state:
    st.session_state.client = None

# Available categories
AVAILABLE_CATEGORIES = [
    'Science', 'History', 'Geography', 'Sports', 'Movies', 'Music',
    'Literature', 'Art', 'Technology', 'Food', 'Animals', 'Space'
]

def generate_questions():
    """Generate QUIZ questions using Gemini API"""
    if not st.session_state.categories:
        st.error("⚠️ Please select at least one category!")
        return
    
    st.session_state.game_state = 'loading'
    
    categories_str = ', '.join(st.session_state.categories)
    prompt = f"""Generate exactly {st.session_state.num_questions} quiz questions with these specifications:
    - Categories: {categories_str}
    - Difficulty: {st.session_state.difficulty}
    - Format: Multiple choice with 4 options

    Respond ONLY with a valid JSON object in this exact format:
    {{
    "questions": [
        {{
        "question": "What is the chemical symbol for gold?",
        "options": ["Au", "Ag", "Go", "Gd"],
        "correctAnswer": 0,
        "category": "Science"
        }}
    ]
    }}

    Make sure each question has exactly 4 plausible options and correctAnswer is the index (0-3) of the correct option.
    DO NOT include any text before or after the JSON."""
        
    try:
        response = st.session_state.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        json_text = response.text.strip()
        if json_text.startswith('```'):
            json_text = json_text.split('```')[1]
            if json_text.startswith('json'):
                json_text = json_text[4:]
        
        questions_data = json.loads(json_text)
        
        if 'questions' in questions_data:
            st.session_state.questions = questions_data['questions']
            st.session_state.game_state = 'playing'
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.session_state.answers = []
            st.session_state.show_answer = False
            st.session_state.selected_answer = None
            st.rerun()
        else:
            st.error("❌ Invalid response format")
            st.session_state.game_state = 'setup'
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.session_state.game_state = 'setup'

# Main UI
st.title("🎯 AI Quiz Game App")
st.markdown("Test your knowledge with AI-generated Quiz questions powered by LLM")

# API Key configuration
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    api_key = st.text_input("Enter your Gemini API Key:", type="password", 
                            help="Get your free API key from https://aistudio.google.com/app/apikey")

if api_key:
    if st.session_state.client is None:
        st.session_state.client = genai.Client(api_key=api_key)
else:
    st.warning("⚠️ Please enter your API key to continue")
    st.stop()

st.divider()

# SETUP SCREEN
if st.session_state.game_state == 'setup':
    st.header("⚙️ Game Setup")
    
    # Category selection
    st.subheader("📚 Select Categories")
    cols = st.columns(3)
    for idx, category in enumerate(AVAILABLE_CATEGORIES):
        with cols[idx % 3]:
            if st.checkbox(category, key=f"cat_{category}"):
                if category not in st.session_state.categories:
                    st.session_state.categories.append(category)
            else:
                if category in st.session_state.categories:
                    st.session_state.categories.remove(category)
    
    if st.session_state.categories:
        st.success(f"Selected: {', '.join(st.session_state.categories)}")
    
    # Difficulty selection
    st.subheader("🎚️ Select Difficulty")
    st.session_state.difficulty = st.radio(
        "Choose difficulty level:",
        ['easy', 'medium', 'hard'],
        index=1,
        horizontal=True
    )
    
    # Number of questions
    st.subheader("🔢 Number of Questions")
    st.session_state.num_questions = st.select_slider(
        "How many questions?",
        options=[3, 5, 10, 15, 20],
        value=3
    )
    
    st.divider()
    
    if st.button("🚀 Start Game", type="primary", use_container_width=True):
        generate_questions()

# LOADING SCREEN
elif st.session_state.game_state == 'loading':
    st.header("⏳ Generating Questions...")
    with st.spinner("Creating your quiz challenge..."):
        pass

# PLAYING SCREEN
elif st.session_state.game_state == 'playing':
    question = st.session_state.questions[st.session_state.current_question]
    
    # Progress bar
    progress = (st.session_state.current_question + 1) / len(st.session_state.questions)
    st.progress(progress)
    
    # Header with question number and score
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Question", f"{st.session_state.current_question + 1} of {len(st.session_state.questions)}")
    with col2:
        st.metric("Score", st.session_state.score)
    
    st.divider()
    
    # Category badge
    st.markdown(f"**Category:** `{question['category']}`")
    
    # Question text
    st.subheader(question['question'])
    st.write("")  # Spacing
    
    # Answer options
    for idx, option in enumerate(question['options']):
        option_label = f"{chr(65 + idx)}. {option}"
        
        # Determine button appearance based on state
        if st.session_state.show_answer:
            # Show correct/incorrect feedback
            if idx == question['correctAnswer']:
                if st.session_state.selected_answer == idx:
                    st.success(f"✅ {option_label} - CORRECT!")
                else:
                    st.info(f"✓ {option_label} - Correct Answer")
            elif st.session_state.selected_answer == idx:
                st.error(f"❌ {option_label} - Wrong")
            else:
                st.write(option_label)
        else:
            # Interactive buttons
            if st.button(
                option_label,
                key=f"option_{idx}",
                type="primary" if st.session_state.selected_answer == idx else "secondary",
                use_container_width=True
            ):
                st.session_state.selected_answer = idx
                st.rerun()
    
    st.divider()
    
    # Next button logic
    def next_question():
        if st.session_state.selected_answer is None:
            st.warning("⚠️ Please select an answer!")
            return
        
        if not st.session_state.show_answer:
            # First click - show the answer
            st.session_state.show_answer = True
            st.rerun()
            return
        
        # Record the answer
        is_correct = st.session_state.selected_answer == question['correctAnswer']
        st.session_state.answers.append({
            'questionIndex': st.session_state.current_question,
            'selectedAnswer': st.session_state.selected_answer,
            'isCorrect': is_correct
        })
        
        if is_correct:
            st.session_state.score += 1
        
        # Move to next question or results
        if st.session_state.current_question + 1 < len(st.session_state.questions):
            st.session_state.current_question += 1
            st.session_state.selected_answer = None
            st.session_state.show_answer = False
            st.rerun()
        else:
            st.session_state.game_state = 'results'
            st.rerun()
    
    # Button text changes based on state
    button_text = "Check Answer" if not st.session_state.show_answer else \
                  "Finish Game" if st.session_state.current_question + 1 == len(st.session_state.questions) else \
                  "Next Question"
    
    if st.button(button_text, type="primary", use_container_width=True):
        next_question()

# RESULTS SCREEN
elif st.session_state.game_state == 'results':
    percentage = round((st.session_state.score / len(st.session_state.questions)) * 100)
    
    st.header("🏆 Results")
    
    # Score display
    st.metric("Final Score", f"{st.session_state.score}/{len(st.session_state.questions)}", f"{percentage}%")
    
    # Performance message
    if percentage >= 80:
        st.success("🏆 Excellent! You're a quiz master!")
    elif percentage >= 60:
        st.success("👍 Good job! Well done!")
    elif percentage >= 40:
        st.info("👌 Not bad! Keep practicing!")
    else:
        st.warning("📚 Keep studying! You'll do better next time!")
    
    st.divider()
    
    # Detailed results
    st.subheader("📊 Question Review")
    
    for idx, question in enumerate(st.session_state.questions):
        user_answer = st.session_state.answers[idx]
        is_correct = user_answer['isCorrect']
        
        with st.expander(
            f"{'✅' if is_correct else '❌'} Question {idx + 1}: {question['question'][:50]}...",
            expanded=False
        ):
            st.write(f"**Question:** {question['question']}")
            st.write(f"**Your Answer:** {question['options'][user_answer['selectedAnswer']]}")
            
            if not is_correct:
                st.write(f"**Correct Answer:** {question['options'][question['correctAnswer']]}")
    
    st.divider()
    
    # Play again button
    def reset_game():
        st.session_state.game_state = 'setup'
        st.session_state.current_question = 0
        st.session_state.selected_answer = None
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.questions = []
        st.session_state.show_answer = False
        st.rerun()
    
    if st.button("🔄 Play Again", type="primary", use_container_width=True):
        reset_game()
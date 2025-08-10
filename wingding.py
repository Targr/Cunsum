import streamlit as st
import random

# Full mapping with actual Wingdings glyphs (requires Wingdings font installed)
wingdings_map = {
    'A': '✈', 'B': '☀', 'C': '✂', 'D': '✉', 'E': '☎', 'F': '✌', 'G': '✏', 'H': '✒', 'I': '✔', 'J': '✖',
    'K': '✳', 'L': '✴', 'M': '❄', 'N': '❇', 'O': '❌', 'P': '❍', 'Q': '❏', 'R': '❐', 'S': '❑', 'T': '❒',
    'U': '●', 'V': '■', 'W': '▲', 'X': '▼', 'Y': '◆', 'Z': '○',
    '1': '❶', '2': '❷', '3': '❸', '4': '❹', '5': '❺', '6': '❻', '7': '❼', '8': '❽', '9': '❾', '0': '❿',
    '!': '✿', '@': '❁', '#': '❂', '$': '❃', '%': '❄', '^': '❅', '&': '❆', '*': '❇', '(': '❈', ')': '❉'
}

categories = {
    'Letters': [chr(65 + i) for i in range(26)],
    'Numbers': list('1234567890'),
    'Symbols': list('!@#$%^&*()')
}

# Initialize session state
if 'letter_pool' not in st.session_state:
    st.session_state.selected_category = 'All'
    st.session_state.letter_pool = list(wingdings_map.keys())
    st.session_state.letter_counts = {letter: 0 for letter in wingdings_map}
    st.session_state.current_letter = None
    st.session_state.mode = None
    st.session_state.message = ""

# Category selection
category_choice = st.selectbox("Choose training category:", ['All'] + list(categories.keys()))
if category_choice != st.session_state.selected_category:
    st.session_state.selected_category = category_choice
    if category_choice == 'All':
        st.session_state.letter_pool = list(wingdings_map.keys())
    else:
        st.session_state.letter_pool = categories[category_choice][:]
    st.session_state.letter_counts = {letter: 0 for letter in st.session_state.letter_pool}
    st.session_state.current_letter = None

# Pick a new challenge
def pick_new_challenge():
    if not st.session_state.letter_pool:
        st.session_state.current_letter = None
        return
    st.session_state.mode = random.choice(['wingdings_to_english', 'english_to_wingdings'])
    st.session_state.current_letter = random.choice(st.session_state.letter_pool)

if st.session_state.current_letter is None:
    pick_new_challenge()

# CSS for Wingdings font
st.markdown("""
<style>
.wingdings {
    font-family: 'Wingdings', sans-serif;
    font-size: 50px;
}
.symbol-box {
    padding: 20px;
    border: 2px solid #ccc;
    border-radius: 10px;
    display: inline-block;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Game UI
if not st.session_state.letter_pool:
    st.success("🎉 You have mastered all letters and symbols in this category!")
else:
    letter = st.session_state.current_letter
    if st.session_state.mode == 'wingdings_to_english':
        st.markdown(f"<div class='symbol-box wingdings'>{wingdings_map[letter]}</div>", unsafe_allow_html=True)
        user_input = st.text_input("Type the English letter or symbol:", key="input1")
    else:
        st.markdown(f"<div class='symbol-box'>{letter}</div>", unsafe_allow_html=True)
        user_input = st.text_input("Type the matching Wingdings symbol:", key="input2")

    if st.button("Submit"):
        correct = False
        if st.session_state.mode == 'wingdings_to_english':
            if user_input.strip().upper() == letter:
                correct = True
        else:
            if user_input.strip() == wingdings_map[letter]:
                correct = True

        if correct:
            st.session_state.letter_counts[letter] += 1
            if st.session_state.letter_counts[letter] >= 3:
                st.session_state.letter_pool.remove(letter)
            st.success("✅ Correct!")
        else:
            st.error("❌ Incorrect.")

        pick_new_challenge()

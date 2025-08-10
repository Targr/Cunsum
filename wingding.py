import streamlit as st
import random

# Full mapping with actual Wingdings glyphs (requires Wingdings font installed)
wingdings_map = {
    'a': '✈', 'b': '☀', 'c': '✂', 'd': '✉', 'e': '☎', 'f': '✌', 'g': '✏', 'h': '✒', 'i': '✔', 'j': '✖',
    'k': '✳', 'l': '✴', 'm': '❄', 'n': '❇', 'o': '❌', 'p': '❍', 'q': '❏', 'r': '❐', 's': '❑', 't': '❒',
    'u': '●', 'v': '■', 'w': '▲', 'x': '▼', 'y': '◆', 'z': '○'
}

categories = {
    'letters': list(wingdings_map.keys())
}

# Initialize session state
if 'letter_pool' not in st.session_state:
    st.session_state.selected_category = 'letters'
    st.session_state.letter_pool = list(wingdings_map.keys())
    st.session_state.letter_counts = {letter: 0 for letter in wingdings_map}
    st.session_state.current_letter = None
    st.session_state.message = ""

# Category selection
category_choice = st.selectbox("choose training category", list(categories.keys()))
if category_choice != st.session_state.selected_category:
    st.session_state.selected_category = category_choice
    st.session_state.letter_pool = categories[category_choice][:]
    st.session_state.letter_counts = {letter: 0 for letter in st.session_state.letter_pool}
    st.session_state.current_letter = None

# Pick a new challenge
def pick_new_challenge():
    if not st.session_state.letter_pool:
        st.session_state.current_letter = None
        return
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
    st.success("you have mastered all letters in this category")
else:
    letter = st.session_state.current_letter
    st.markdown(f"<div class='symbol-box wingdings'>{wingdings_map[letter]}</div>", unsafe_allow_html=True)
    user_input = st.text_input("type the matching letter", key="input1")

    if st.button("submit"):
        if user_input.strip().lower() == letter:
            st.session_state.letter_counts[letter] += 1
            if st.session_state.letter_counts[letter] >= 3:
                st.session_state.letter_pool.remove(letter)
            st.success("correct")
        else:
            st.error(f"incorrect. the correct answer was {letter}")

        pick_new_challenge()

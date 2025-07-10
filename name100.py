import streamlit as st
import time
import requests
import pandas as pd
from datetime import datetime

# App state
if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.names = [""] * 100
    st.session_state.current_index = 0
    st.session_state.start_time = 0.0
    st.session_state.end_time = 0.0
    st.session_state.times_up = False
    st.session_state.entered_names = set()

# Function to validate name with Wikidata and check if they are women
@st.cache_data(show_spinner=False)
def validate_name(name):
    if not name.strip():
        return False
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={name}&language=en&format=json"
    r = requests.get(url)
    if r.status_code == 200:
        results = r.json().get('search', [])
        for result in results:
            qid = result.get('id')
            if qid:
                entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
                entity_data = requests.get(entity_url).json()
                claims = entity_data['entities'][qid]['claims']
                # P21 is 'sex or gender', Q6581072 is 'female'
                if 'P21' in claims:
                    for gender_claim in claims['P21']:
                        gender_id = gender_claim['mainsnak']['datavalue']['value']['id']
                        if gender_id == 'Q6581072':
                            return True
    return False

# Leaderboard
LEADERBOARD_FILE = "leaderboard.csv"

# Stats function
@st.cache_data

def load_leaderboard():
    try:
        return pd.read_csv(LEADERBOARD_FILE)
    except:
        return pd.DataFrame(columns=["username", "email", "time", "timestamp", "names"])

leaderboard = load_leaderboard()

st.set_page_config(page_title="Name 100 Women", layout="centered")

# Main logic
if not st.session_state.started:
    st.title("Can you name 100 women?")
    if st.button("Yes"):
        st.session_state.started = True
        st.session_state.start_time = time.perf_counter()
        st.rerun()
else:
    st.title("Name 100 Women")
    col1, col2 = st.columns([3, 1])

    current_time = time.perf_counter()
    elapsed_time = current_time - st.session_state.start_time

    col2.metric("Time", f"{elapsed_time:.3f} sec")

    # Display entered names to avoid duplicates
    with st.expander("Names you've already entered"):
        st.write(list(st.session_state.entered_names))

    # Entry input
    with col1:
        name_input = st.text_input(f"Enter name #{st.session_state.current_index + 1}", key=f"name_{st.session_state.current_index}")

    if name_input and st.session_state.current_index < 100:
        if name_input in st.session_state.entered_names:
            st.warning("You've already entered that name. Try a new one.")
        elif st.session_state.names[st.session_state.current_index] != name_input:
            if validate_name(name_input):
                st.session_state.names[st.session_state.current_index] = name_input
                st.session_state.entered_names.add(name_input)
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.warning("Name not found as a woman on Wikidata. Try again.")

    if st.session_state.current_index >= 100 and not st.session_state.times_up:
        st.session_state.end_time = time.perf_counter()
        st.session_state.times_up = True
        st.balloons()

    if st.session_state.times_up:
        final_time = st.session_state.end_time - st.session_state.start_time
        st.success(f"You did it in {final_time:.3f} seconds!")

        with st.form("submit_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            submit = st.form_submit_button("Submit to Leaderboard")

            if submit and username and email:
                new_entry = pd.DataFrame({
                    "username": [username],
                    "email": [email],
                    "time": [final_time],
                    "timestamp": [datetime.now().isoformat()],
                    "names": [";".join(st.session_state.names)]
                })
                leaderboard = pd.concat([leaderboard, new_entry], ignore_index=True)
                leaderboard.sort_values(by="time", inplace=True)
                leaderboard.to_csv(LEADERBOARD_FILE, index=False)
                st.success("Submitted!")

    if st.session_state.times_up:
        st.header("Leaderboard")
        st.dataframe(leaderboard[['username', 'time']].head(10))

        st.header("Most Commonly Named Women")
        all_names = ";".join(leaderboard['names'].dropna()).split(";")
        name_counts = pd.Series(all_names).value_counts().head(10)
        st.table(name_counts.reset_index().rename(columns={"index": "Name", 0: "Frequency"}))

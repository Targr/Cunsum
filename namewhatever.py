import streamlit as st
import time
import requests
import pandas as pd
from datetime import datetime
import os

# App state
if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.names = []
    st.session_state.current_index = 0
    st.session_state.start_time = 0.0
    st.session_state.end_time = 0.0
    st.session_state.times_up = False
    st.session_state.entered_names = set()
    st.session_state.category = ""
    st.session_state.target_count = 0
    st.session_state.valid_targets = set()

# Validate name dynamically based on category
@st.cache_data(show_spinner=False)
def validate_name_against_category(name, category):
    if not name.strip():
        return False

    search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={name}&language=en&format=json"
    response = requests.get(search_url)
    if response.status_code != 200:
        return False
    results = response.json().get("search", [])

    for result in results:
        qid = result.get("id")
        if not qid:
            continue
        entity_url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        entity_data = requests.get(entity_url).json()
        claims = entity_data['entities'][qid].get('claims', {})

        # Special case for women
        if category.strip().lower() == 'women':
            if 'P21' in claims:
                for gender_claim in claims['P21']:
                    gender_id = gender_claim['mainsnak']['datavalue']['value']['id']
                    if gender_id in ['Q6581072', 'Q1052281']:  # female or transgender female
                        return True

        else:
            cat_search = requests.get(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={category}&language=en&format=json&type=item").json()
            if not cat_search['search']:
                return False
            cat_qid = cat_search['search'][0]['id']
            # Match P31 or any P279 ancestry
            if 'P31' in claims:
                for inst in claims['P31']:
                    if inst['mainsnak'].get('datavalue'):
                        inst_id = inst['mainsnak']['datavalue']['value']['id']
                        if check_subclass_or_equal(inst_id, cat_qid):
                            return True
    return False

# Check subclass relationship
@st.cache_data(show_spinner=False)
def check_subclass_or_equal(child_id, parent_id):
    sparql = f"""
    ASK {{
      wd:{child_id} wdt:P279* wd:{parent_id} .
    }}
    """
    endpoint = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    response = requests.get(endpoint, params={"query": sparql}, headers=headers)
    return response.json().get("boolean", False)

# Load leaderboard from file
def load_leaderboard():
    if os.path.exists("leaderboard.csv"):
        return pd.read_csv("leaderboard.csv")
    else:
        return pd.DataFrame(columns=["username", "email", "time", "timestamp", "names"])

# Game start screen
st.set_page_config(page_title="Name That Thing!", layout="centered")

if not st.session_state.started:
    st.title("Create Your Naming Challenge")
    st.session_state.category = st.text_input("What do you want to name? (e.g., mammals, women, Olympic sports)")
    st.session_state.target_count = st.number_input("How many do you want to name?", min_value=1, max_value=100, step=1)
    if st.button("Start Game") and st.session_state.category:
        st.session_state.names = [""] * st.session_state.target_count
        st.session_state.entered_names = set()
        st.session_state.current_index = 0
        st.session_state.start_time = time.perf_counter()
        st.session_state.started = True
        st.rerun()
else:
    st.title(f"Name {st.session_state.target_count} Things from: {st.session_state.category}")
    col1, col2 = st.columns([3, 1])

    current_time = time.perf_counter()
    elapsed_time = current_time - st.session_state.start_time
    col2.metric("Time", f"{elapsed_time:.3f} sec")

    with st.expander("Names you've already entered"):
        st.write(list(st.session_state.entered_names))

    name_key = f"name_{st.session_state.current_index}"
    if f"_focus_{name_key}" not in st.session_state:
        st.session_state[f"_focus_{name_key}"] = True

    with col1:
        name_input = st.text_input(
            f"Enter item #{st.session_state.current_index + 1}",
            key=name_key,
            label_visibility="visible",
        )

    if name_input and st.session_state.current_index < st.session_state.target_count:
        lower_input = name_input.strip().lower()
        if lower_input in st.session_state.entered_names:
            st.warning("You've already entered that. Try a new one.")
        elif st.session_state.names[st.session_state.current_index] != name_input:
            if validate_name_against_category(name_input, st.session_state.category):
                st.session_state.names[st.session_state.current_index] = name_input
                st.session_state.entered_names.add(lower_input)
                st.session_state.current_index += 1
                st.session_state[f"_focus_name_{st.session_state.current_index}"] = True
                st.rerun()
            else:
                st.warning("That doesn't match the category on Wikidata. Try again.")

    if st.session_state.current_index >= st.session_state.target_count and not st.session_state.times_up:
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
                leaderboard = pd.concat([load_leaderboard(), new_entry], ignore_index=True)
                leaderboard.sort_values(by="time", inplace=True)
                leaderboard.to_csv("leaderboard.csv", index=False)
                st.success("Submitted!")

        st.header("Leaderboard")
        st.dataframe(load_leaderboard()[['username', 'time']].head(10))

        st.header(f"Most Commonly Named from {st.session_state.category}")
        all_names = ";".join(load_leaderboard()['names'].dropna()).split(";")
        name_counts = pd.Series(all_names).value_counts().head(10)
        st.table(name_counts.reset_index().rename(columns={"index": "Name", 0: "Frequency"}))

# Streamlined Streamlit Naming Challenge Game
import streamlit as st
import time
import requests
import pandas as pd
from datetime import datetime
import os
import re
import inflect
import time as systime

p = inflect.engine()

# --- App State --- #
if 'started' not in st.session_state:
    st.session_state.update({
        'started': False,
        'names': [],
        'current_index': 0,
        'start_time': 0.0,
        'end_time': 0.0,
        'times_up': False,
        'entered_names': set(),
        'category': "",
        'target_count': 0,
        'cat_qid': None
    })

# --- Utilities --- #
def normalize(text):
    return p.singular_noun(text.lower().strip()) or text.lower().strip()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@st.cache_data(show_spinner=False)
def get_category_qid(category):
    try:
        r = requests.get(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={category}&language=en&format=json&type=item")
        if r.ok and r.text.strip():
            for item in r.json().get('search', []):
                if item.get('id') and 'disambiguation' not in item.get('description', '').lower():
                    return item['id']
    except:
        pass
    return None

@st.cache_data(show_spinner=False)
def check_subclass_or_equal(child_id, parent_id):
    try:
        query = f"""ASK {{ wd:{child_id} wdt:P279* wd:{parent_id} . }}"""
        r = requests.get("https://query.wikidata.org/sparql", params={"query": query}, headers={"Accept": "application/sparql-results+json"})
        return r.ok and r.json().get("boolean", False)
    except:
        return False

@st.cache_data(show_spinner=False)
def validate_name(name, category, cat_qid):
    if not name or not cat_qid:
        return False
    try:
        r = requests.get(f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={name}&language=en&format=json")
        for result in r.json().get("search", []):
            qid = result.get("id")
            if not qid:
                continue
            detail = requests.get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")
            claims = detail.json()['entities'][qid].get('claims', {})
            if 'P31' in claims:
                if any(c['mainsnak'].get('datavalue', {}).get('value', {}).get('id') == 'Q4167410' for c in claims['P31']):
                    continue
                for inst in claims['P31']:
                    try:
                        inst_id = inst['mainsnak']['datavalue']['value']['id']
                        if check_subclass_or_equal(inst_id, cat_qid):
                            return True
                    except:
                        continue
            if category == 'women' and 'P21' in claims:
                for g in claims['P21']:
                    if g['mainsnak']['datavalue']['value']['id'] in ['Q6581072', 'Q1052281']:
                        return True
    except:
        pass
    return False

# --- Leaderboard --- #
def load_leaderboard():
    return pd.read_csv("leaderboard.csv") if os.path.exists("leaderboard.csv") else pd.DataFrame(columns=["username", "email", "time", "timestamp", "names"])

def save_leaderboard(df):
    df.to_csv("leaderboard.csv", index=False)

# --- App UI --- #
st.set_page_config("Name That Thing!", layout="centered")

if st.button("Restart Game"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()

if not st.session_state.started:
    st.title("Create Your Naming Challenge")
    cat_input = st.text_input("Enter a category (e.g., mammals, Olympic sports):")
    count = st.number_input("How many do you want to name?", min_value=1, max_value=100, step=1)

    if st.button("Start Game") and cat_input:
        st.session_state.category = normalize(cat_input)
        st.session_state.cat_qid = get_category_qid(st.session_state.category)
        if not st.session_state.cat_qid:
            st.error("Couldn't find a matching category on Wikidata.")
        else:
            st.session_state.target_count = count
            st.session_state.names = [""] * count
            st.session_state.current_index = 0
            st.session_state.entered_names = set()
            st.session_state.start_time = time.perf_counter()
            st.session_state.started = True
            st.rerun()
else:
    st.title(f"Name {st.session_state.target_count} Things from: {st.session_state.category}")
    col1, col2 = st.columns([3, 1])
    col2.metric("Time", f"{time.perf_counter() - st.session_state.start_time:.3f} sec")

    with st.expander("Names you've already entered"):
        st.write(list(st.session_state.entered_names))

    name_key = f"name_{st.session_state.current_index}"
    name_input = col1.text_input(f"Enter item #{st.session_state.current_index + 1}", key=name_key)

    if name_input and st.session_state.current_index < st.session_state.target_count:
        norm = normalize(name_input)
        if norm in st.session_state.entered_names:
            st.warning("Duplicate entry.")
        elif validate_name(name_input, st.session_state.category, st.session_state.cat_qid):
            st.session_state.names[st.session_state.current_index] = name_input
            st.session_state.entered_names.add(norm)
            st.session_state.current_index += 1
            st.rerun()
        else:
            st.warning("Invalid according to Wikidata.")

    if st.session_state.current_index >= st.session_state.target_count and not st.session_state.times_up:
        st.session_state.end_time = time.perf_counter()
        st.session_state.times_up = True
        st.balloons()

    if st.session_state.times_up:
        duration = st.session_state.end_time - st.session_state.start_time
        st.success(f"Completed in {duration:.3f} seconds!")

        with st.form("submit_form"):
            user = st.text_input("Username")
            email = st.text_input("Email")
            submit = st.form_submit_button("Submit to Leaderboard")
            if submit:
                if not (user and email):
                    st.error("Both fields required.")
                elif not is_valid_email(email):
                    st.error("Enter valid email.")
                else:
                    entry = pd.DataFrame({
                        "username": [user],
                        "email": [email],
                        "time": [duration],
                        "timestamp": [datetime.now().isoformat()],
                        "names": [";".join(st.session_state.names)]
                    })
                    board = pd.concat([load_leaderboard(), entry], ignore_index=True)
                    board.sort_values(by="time", inplace=True)
                    save_leaderboard(board)
                    st.success("Submitted!")

        st.header("Leaderboard")
        st.dataframe(load_leaderboard()[["username", "time"]].head(10))

        st.header(f"Most Commonly Named from {st.session_state.category}")
        all_names = ";".join(load_leaderboard()['names'].dropna()).split(";")
        name_counts = pd.Series(all_names).value_counts().head(10)
        st.table(name_counts.reset_index().rename(columns={"index": "Name", 0: "Frequency"}))

import streamlit as st
import time
import requests
import pandas as pd
from datetime import datetime

# --- Utilities ---
@st.cache_data(show_spinner=False)
def fetch_category_suggestions(prefix):
    if not prefix:
        return []
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "namespace": 14,
        "search": prefix,
        "limit": 10,
        "format": "json"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()
        return [r.replace("Category:", "") for r in results[1]]
    return []

@st.cache_data(show_spinner=False)
def fetch_valid_category_members(category):
    url = "https://en.wikipedia.org/w/api.php"
    members = []
    cmcontinue = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": 500,
            "format": "json"
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
        r = requests.get(url, params=params)
        if r.status_code != 200:
            break
        data = r.json()
        members += [m["title"] for m in data["query"]["categorymembers"] if not m["title"].startswith("Category:")]
        cmcontinue = data.get("continue", {}).get("cmcontinue")
        if not cmcontinue:
            break
    return members

@st.cache_data(show_spinner=False)
def validate_name(name, category):
    if not name.strip():
        return False
    url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={name}&language=en&format=json"
    r = requests.get(url)
    if r.status_code == 200:
        results = r.json().get('search', [])
        for result in results:
            qid = result.get('id')
            if qid:
                page_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=categories&format=json&titles={name}"
                resp = requests.get(page_url)
                if resp.status_code == 200:
                    pages = resp.json().get("query", {}).get("pages", {})
                    for page in pages.values():
                        categories = [c['title'].replace("Category:", "").lower() for c in page.get("categories", [])]
                        if category.lower() in categories:
                            return True
    return False

@st.cache_data
def load_leaderboard():
    try:
        return pd.read_csv("leaderboard.csv")
    except:
        return pd.DataFrame(columns=["username", "email", "time", "timestamp", "names", "category", "target_count"])

# --- App State ---
if 'started' not in st.session_state:
    st.session_state.started = False
    st.session_state.names = []
    st.session_state.current_index = 0
    st.session_state.start_time = 0.0
    st.session_state.end_time = 0.0
    st.session_state.times_up = False
    st.session_state.entered_names = set()
    st.session_state.category = ""
    st.session_state.target_count = 100
    st.session_state.valid_members = []

leaderboard = load_leaderboard()
st.set_page_config(page_title="Name by Wikipedia Category", layout="centered")

# --- UI: Initial Setup ---
if not st.session_state.started:
    st.title("Can you name people from a Wikipedia category?")

    category_input = st.text_input("Search for a Wikipedia category:")
    suggestions = fetch_category_suggestions(category_input)
    if suggestions:
        selected = st.selectbox("Matching categories:", suggestions)
        if selected:
            st.session_state.category = selected
            st.session_state.valid_members = fetch_valid_category_members(selected)
            st.success(f"Selected category: {selected}")

    st.session_state.target_count = st.number_input("How many names?", min_value=1, max_value=500, value=100, step=1)

    if st.button("Start") and st.session_state.category:
        st.session_state.started = True
        st.session_state.start_time = time.perf_counter()
        st.session_state.names = [""] * st.session_state.target_count
        st.rerun()

# --- UI: Game Logic ---
else:
    st.title(f"Name {st.session_state.target_count} from '{st.session_state.category}'")
    col1, col2 = st.columns([3, 1])

    current_time = time.perf_counter()
    elapsed_time = current_time - st.session_state.start_time
    col2.metric("Time", f"{elapsed_time:.3f} sec")

    with st.expander("Names you've already entered"):
        st.write(list(st.session_state.entered_names))

    with st.expander("See all possible valid names"):
        st.write(st.session_state.valid_members[:100])  # only show first 100 for performance

    name_key = f"name_{st.session_state.current_index}"
    if f"_focus_{name_key}" not in st.session_state:
        st.session_state[f"_focus_{name_key}"] = True

    with col1:
        name_input = st.text_input(f"Enter name #{st.session_state.current_index + 1}", key=name_key)

    if name_input and st.session_state.current_index < st.session_state.target_count:
        if name_input in st.session_state.entered_names:
            st.warning("You've already entered that name. Try a new one.")
        elif st.session_state.names[st.session_state.current_index] != name_input:
            if validate_name(name_input, st.session_state.category):
                st.session_state.names[st.session_state.current_index] = name_input
                st.session_state.entered_names.add(name_input)
                st.session_state.current_index += 1
                st.session_state[f"_focus_name_{st.session_state.current_index}"] = True
                st.rerun()
            else:
                st.warning("Name not found in selected category on Wikipedia. Try again.")

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
                    "names": [";".join(st.session_state.names)],
                    "category": [st.session_state.category],
                    "target_count": [st.session_state.target_count]
                })
                leaderboard = pd.concat([leaderboard, new_entry], ignore_index=True)
                leaderboard.sort_values(by="time", inplace=True)
                leaderboard.to_csv("leaderboard.csv", index=False)
                st.success("Submitted!")

    if st.session_state.times_up:
        st.header("Leaderboard")
        filtered = leaderboard[leaderboard["category"] == st.session_state.category]
        st.dataframe(filtered[['username', 'time']].head(10))

        st.header(f"Most Common in '{st.session_state.category}'")
        all_names = ";".join(filtered['names'].dropna()).split(";")
        name_counts = pd.Series(all_names).value_counts().head(10)
        st.table(name_counts.reset_index().rename(columns={"index": "Name", 0: "Frequency"}))

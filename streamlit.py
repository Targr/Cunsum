import streamlit as st
import random
import requests
from collections import defaultdict

# --- Initial Setup --- #
if 'likes' not in st.session_state:
    st.session_state.likes = set()

if 'qualities' not in st.session_state:
    st.session_state.qualities = set()
    st.session_state.quality_scores = defaultdict(float)
    st.session_state.quality_frequency = defaultdict(int)
    st.session_state.image_history = []
    st.session_state.interacted_images = []
    st.session_state.ignored_images = defaultdict(int)
    st.session_state.coins = 0
    st.session_state.generation_count = 0
    st.session_state.decay_rate = 0.95
    st.session_state.background_cost = 5
    st.session_state.nI = 32
    st.session_state.last_displayed = []
    st.session_state.pending_hybrid = []

# --- API Access Keys --- #
PEXELS_API_KEY = '1ySgrjZpx7gT5Hml4mfF3i6WbzXo1XYZcRBYv3zfRJsD3poUxGVNyFGs'

# --- Image Scraper --- #
def get_pexels_images(query_tags, num_images):
    query = random.choice(query_tags)  # use one tag at a time for Pexels
    try:
        url = f"https://api.pexels.com/v1/search?query={query}&per_page={num_images}"
        headers = {"Authorization": PEXELS_API_KEY}
        response = requests.get(url, headers=headers)
        data = response.json()
        return [{"id": str(img['id']), "url": img['src']['medium'], "qualities": query_tags} for img in data.get('photos', [])]
    except Exception as e:
        st.warning(f"Pexels error for '{query}': {e}")
        return []

def get_new_images(num):
    tag_pool = [
        'sunset', 'robot', 'cyberpunk', 'vintage', 'macro', 'mountains', 'cats', 'dogs',
        'sci-fi', 'neon', 'portrait', 'food', 'minimalist', 'graffiti', 'space',
        'fantasy', 'surreal', 'cityscape', 'wildlife', 'pattern', 'texture', 'ocean', 'forest', 'desert', 'night'
    ]

    images = []
    for _ in range(num * 2):
        pexels_tags = random.sample(tag_pool, k=random.randint(2, 3))
        images.extend(get_pexels_images(pexels_tags, 1))

    random.shuffle(images)
    return images[:num]

# --- Main Streamlit App --- #
st.title("🔼️ Image Preference Explorer")
st.write("Interact with images to shape your preferences.")

with st.sidebar:
    st.markdown("### 🔍 Your Top Preferences")
    top = sorted(st.session_state.quality_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    for q, score in top:
        st.write(f"**{q}**: {score:.2f}")

if st.button("🔄 Refresh / More Images") or not st.session_state.last_displayed:
    interactions = list(st.session_state.likes)
    expected = int(st.session_state.nI * 0.4)
    if len(interactions) == expected:
        st.session_state.coins += 1
        st.success(f"🪙 Coin earned! Total coins: {st.session_state.coins}")

    st.session_state.image_history.extend(st.session_state.last_displayed)

    for img in interactions:
        for q in img['qualities']:
            st.session_state.qualities.add(q)
            st.session_state.quality_frequency[q] += 1
            rarity = 1 / max(1, st.session_state.quality_frequency[q])
            st.session_state.quality_scores[q] += 1.0 * rarity

    for img in st.session_state.last_displayed:
        if img not in interactions:
            st.session_state.ignored_images[img['id']] += 1

    recently_used = {q for img in interactions for q in img['qualities']}
    for q in st.session_state.quality_scores:
        if q not in recently_used:
            st.session_state.quality_scores[q] *= st.session_state.decay_rate

    st.session_state.generation_count += 1
    insert_weird = st.session_state.generation_count % 5 == 0
    all_imgs = get_new_images(50)

    if insert_weird:
        top_qualities = sorted(st.session_state.quality_scores, key=st.session_state.quality_scores.get, reverse=True)[:10]
        weird_image = next((img for img in all_imgs if not any(q in top_qualities for q in img['qualities'])), None)
        selected_images = sorted(all_imgs, key=lambda img: sum(st.session_state.quality_scores[q] for q in img['qualities']), reverse=True)[:st.session_state.nI-1]
        if weird_image:
            selected_images.append(weird_image)
    else:
        selected_images = sorted(all_imgs, key=lambda img: sum(st.session_state.quality_scores[q] for q in img['qualities']), reverse=True)[:st.session_state.nI]

    st.session_state.last_displayed = selected_images
    st.session_state.interacted_images = []
    st.session_state.likes = set()

st.write("## Images")
cols = st.columns(4)
for idx, img in enumerate(st.session_state.last_displayed):
    with cols[idx % 4]:
        st.image(img['url'], caption=", ".join(img['qualities']), use_container_width=True)
        liked = st.checkbox("Like", key=f"like-{img['id']}")
        if liked:
            st.session_state.likes.add(img)
        elif img in st.session_state.likes:
            st.session_state.likes.remove(img)

if st.session_state.coins >= st.session_state.background_cost:
    if st.button("🎨 Redeem Background"):
        top_qualities = sorted(st.session_state.quality_scores, key=st.session_state.quality_scores.get, reverse=True)[:5]
        st.balloons()
        st.success(f"New background generated from: {top_qualities}")
        example_images = get_pexels_images(random.sample(top_qualities, k=2), 3)
        for ex_img in example_images:
            st.image(ex_img['url'], caption=", ".join(ex_img['qualities']), use_container_width=True)
        st.session_state.coins -= st.session_state.background_cost

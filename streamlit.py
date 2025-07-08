# This is a scaffold of the image preference discovery system in Python

import random
import requests
from collections import defaultdict, Counter

# --- Initial Setup --- #
qualities = set()
quality_scores = defaultdict(float)
quality_frequency = defaultdict(int)
image_history = []
interacted_images = []
ignored_images = defaultdict(int)
coins = 0
generation_count = 0
decay_rate = 0.95
background_cost = 5
nI = 32  # Initial batch size, to be dynamically updated later

# --- API Access Keys --- #
UNSPLASH_ACCESS_KEY = 'lYR5e42tHGOQEwaHBFg3F0A0EMSfd0LyaF37eZCGBPg'
PEXELS_API_KEY = '1ySgrjZpx7gT5Hml4mfF3i6WbzXo1XYZcRBYv3zfRJsD3poUxGVNyFGs'

# --- Image Scrapers --- #
def get_unsplash_images(query, num_images):
    url = "https://api.unsplash.com/search/photos"
    params = {
        'query': query,
        'per_page': num_images,
        'client_id': UNSPLASH_ACCESS_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return [{"id": img['id'], "url": img['urls']['regular'], "qualities": [query]} for img in data.get('results', [])]

def get_pexels_images(query, num_images):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page={num_images}"
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    return [{"id": str(img['id']), "url": img['src']['medium'], "qualities": [query]} for img in data.get('photos', [])]

def get_new_images(num):
    queries = ['nature', 'abstract', 'animals', 'architecture', 'people']
    query = random.choice(queries)
    images = get_unsplash_images(query, num//2) + get_pexels_images(query, num//2)
    return images[:num]

# --- User Interaction --- #
def show_images_to_user(images):
    print("Showing images:")
    for img in images:
        print(f" - {img['url']} (Qualities: {img['qualities']})")
    for img in images:
        print(f" - {img['id']} (Qualities: {img['qualities']})")

def get_user_interactions(images):
    return [img for img in images if random.random() < 0.4]  # Simulated 40% engagement

def generate_background(preferred_qualities):
    print(f"🎨 New background based on: {preferred_qualities}")

# --- Main Loop --- #
while True:
    generation_count += 1
    insert_weird = generation_count % 5 == 0

    if insert_weird:
        all_imgs = get_new_images(50)
        top_qualities = sorted(quality_scores, key=quality_scores.get, reverse=True)[:10]
        weird_image = next((img for img in all_imgs if not any(q in top_qualities for q in img['qualities'])), None)
        selected_images = sorted(all_imgs, key=lambda img: sum(quality_scores[q] for q in img['qualities']), reverse=True)[:nI-1]
        if weird_image:
            selected_images.append(weird_image)
    else:
        all_imgs = get_new_images(50)
        selected_images = sorted(all_imgs, key=lambda img: sum(quality_scores[q] for q in img['qualities']), reverse=True)[:nI]

    show_images_to_user(selected_images)
    input("Press Enter after interacting...")

    interactions = get_user_interactions(selected_images)
    print(f"Interacted with {len(interactions)} / {len(selected_images)} images")

    image_history.extend(selected_images)
    interacted_images.extend(interactions)

    for img in interactions:
        for q in img['qualities']:
            qualities.add(q)
            quality_frequency[q] += 1
            rarity = 1 / max(1, quality_frequency[q])
            quality_scores[q] += 1.0 * rarity

    for img in selected_images:
        if img not in interactions:
            ignored_images[img['id']] += 1

    recently_used = {q for img in interactions for q in img['qualities']}
    for q in quality_scores:
        if q not in recently_used:
            quality_scores[q] *= decay_rate

    expected = int(nI * 0.4)
    if len(interactions) == expected:
        coins += 1
        print(f"🪙 Coin earned! Total coins: {coins}")

    if coins >= background_cost:
        choice = input("Spend 5 coins on new background? (y/n): ").strip().lower()
        if choice == 'y':
            top_qualities = sorted(quality_scores, key=quality_scores.get, reverse=True)[:5]
            generate_background(top_qualities)
            coins -= background_cost

    print("Press Enter for next round...")
    input()

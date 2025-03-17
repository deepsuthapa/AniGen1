import streamlit as st
import requests

# Set MangaDex API URL
API_URL = "https://api.mangadex.org/manga"
CHAPTER_API_URL = "https://api.mangadex.org/manga/{}/feed"
COVER_URL = "https://uploads.mangadex.org/covers"
LATEST_UPDATES_API = "https://api.mangadex.org/chapter"

st.set_page_config(page_title="MangaUp", layout="wide")

# Function to get latest manga updates
def get_latest_manga(limit=10, search_query=None):
    params = {"limit": limit, "order[updatedAt]": "desc"}
    if search_query:
        params["title"] = search_query
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Retrieve correct cover image of the manga
def get_cover_image(manga):
    try:
        cover_art = next((rel for rel in manga['relationships'] if rel['type'] == 'cover_art'), None)
        if cover_art:
            cover_id = cover_art['id']
            cover_res = requests.get(f"https://api.mangadex.org/cover/{cover_id}")
            if cover_res.status_code == 200:
                cover_filename = cover_res.json().get("data", {}).get("attributes", {}).get("fileName", "")
                return f"{COVER_URL}/{manga['id']}/{cover_filename}"
        return "https://via.placeholder.com/150"
    except:
        return "https://via.placeholder.com/150"

# Function to fetch manga details
def get_manga_details(manga_id):
    response = requests.get(f"{API_URL}/{manga_id}")
    if response.status_code == 200:
        return response.json()["data"]
    return {}

# Function to fetch manga chapters
def get_manga_chapters(manga_id):
    response = requests.get(CHAPTER_API_URL.format(manga_id))
    if response.status_code == 200:
        return sorted(response.json()["data"], key=lambda x: x["attributes"].get("chapter", 0))
    return []

# Function to get latest chapter updates
def get_latest_chapter_updates():
    params = {"limit": 20, "order[publishAt]": "desc"}
    response = requests.get(LATEST_UPDATES_API, params=params)
    if response.status_code == 200:
        return response.json()["data"]
    return []

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "All Updates", "Search Manga", "Manga Reader", "Latest Chapters"])

if page == "Home":
    st.title("MangaUps")
    st.subheader("Latest Updates")
    latest_manga = get_latest_manga()
    
    col1, col2 = st.columns(2)
    for index, manga in enumerate(latest_manga):
        manga_id = manga["id"]
        title = manga["attributes"]["title"].get("en", "Unknown Title")
        desc = manga["attributes"].get("description", {}).get("en", "No description available.")
        cover_url = get_cover_image(manga)
        
        with (col1 if index % 2 == 0 else col2):
            if cover_url:
                st.image(cover_url, caption=title, width=150)
            st.write(f"**{title}**")
            st.write(desc[:200] + "...")
            if st.button(f"Read - {title}", key=f"manga_{manga_id}"):
                st.session_state["selected_manga"] = manga_id
                st.rerun()

elif page == "All Updates":
    st.title("All Manga Updates")
    all_manga = get_latest_manga(limit=20)
    for manga in all_manga:
        manga_id = manga["id"]
        title = manga["attributes"]["title"].get("en", "Unknown Title")
        cover_url = get_cover_image(manga)
        
        if cover_url:
            st.image(cover_url, caption=title, width=150)
        st.write(f"**{title}**")
        if st.button(f"Read - {title}", key=f"updates_{manga_id}"):
            st.session_state["selected_manga"] = manga_id
            st.rerun()

elif page == "Search Manga":
    st.title("Search Manga")
    search_query = st.text_input("Enter manga title")
    if search_query:
        search_results = get_latest_manga(search_query=search_query)
        for manga in search_results:
            manga_id = manga["id"]
            title = manga["attributes"]["title"].get("en", "Unknown Title")
            cover_url = get_cover_image(manga)
            
            if cover_url:
                st.image(cover_url, caption=title, width=150)
            st.write(f"**{title}**")
            if st.button(f"Read - {title}", key=f"search_{manga_id}"):
                st.session_state["selected_manga"] = manga_id
                st.rerun()

elif page == "Manga Reader" and "selected_manga" in st.session_state:
    manga_id = st.session_state["selected_manga"]
    manga_details = get_manga_details(manga_id)
    title = manga_details["attributes"]["title"].get("en", "Unknown Title")
    st.title(title)
    
    cover_url = get_cover_image(manga_details)
    if cover_url:
        st.image(cover_url, caption=title, width=150)
    
    st.subheader("Chapters")
    chapters = get_manga_chapters(manga_id)
    for chapter in chapters:
        chapter_id = chapter["id"]
        chapter_number = chapter["attributes"].get("chapter", "?")
        volume_number = chapter["attributes"].get("volume", "?")
        language = chapter["attributes"].get("translatedLanguage", "Unknown")
        chapter_title = f"Volume {volume_number} - Chapter {chapter_number} ({language})"
        st.write(f"[Read {chapter_title}](https://mangadex.org/chapter/{chapter_id})")

elif page == "Latest Chapters":
    st.title("Latest 24 Hours Updates")
    latest_chapters = get_latest_chapter_updates()
    for chapter in latest_chapters:
        title = chapter["attributes"].get("title", "Unknown Chapter")
        language = chapter["attributes"].get("translatedLanguage", "Unknown")
        st.write(f"**{title}** ({language})")

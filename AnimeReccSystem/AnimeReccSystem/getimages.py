import streamlit as st
import requests

# Streamlit app title
st.title("Anime Search with Suggestions")

# Search input
search_term = st.text_input("Search for an anime:")

# Check if the user has typed a search term
if search_term:
    # Jikan API URL for searching anime
    url = f'https://api.jikan.moe/v4/anime?q={search_term}&limit=10'

    # Make an API request
    response = requests.get(url)

    # Check if the API request was successful
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])

        if results:
            # Loop through the results and display them
            for anime in results:
                st.subheader(anime['title'])  # Display anime title
                st.image(anime['images']['jpg']['large_image_url'], use_column_width=True)  # Display anime image
        else:
            st.write("No results found.")
    else:
        st.write("Error fetching data from the API.")
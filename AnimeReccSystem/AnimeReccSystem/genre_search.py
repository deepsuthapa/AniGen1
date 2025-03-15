import streamlit as st
import pandas as pd

# Load the anime data
anime_data = pd.read_csv('anime.csv')

# Extract unique genres
all_genres = set()
for genres in anime_data['genre'].dropna():
    all_genres.update(genre.strip() for genre in genres.split(','))

# Streamlit app title and description
st.title("Anime Search by Genre")
st.write("Search for anime based on your favorite genres!")

# Genre selection
selected_genres = st.multiselect("Select Genre(s)", sorted(all_genres))

# Filter anime data by selected genres
if selected_genres:
    filtered_data = anime_data[anime_data['genre'].apply(
        lambda x: all(genre in x for genre in selected_genres) if pd.notna(x) else False
    )]

    # Display results
    if not filtered_data.empty:
        st.write(f"### Results ({len(filtered_data)})")
        for _, row in filtered_data.iterrows():
            st.write(f"**{row['name']}** - {row['type']} - {row['episodes']} episodes - Rating: {row['rating']}")
            st.write(f"Genres: {row['genre']}")
            st.write("---")
    else:
        st.write("No results found for the selected genres.")
else:
    st.write("Please select at least one genre to search.")
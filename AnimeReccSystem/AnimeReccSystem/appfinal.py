import numpy as np
import pandas as pd
import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
import requests
from bs4 import BeautifulSoup
import re
import base64  # For encoding the image


# Set background image from a local file with absolute path
def set_background(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded_image = base64.b64encode(data).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Load data and model
def load_data():
    anime = pd.read_csv("https://raw.githubusercontent.com/deepsuthapa/AniGen1/refs/heads/master/AnimeReccSystem/AnimeReccSystem/anime.csv").dropna()
    ratings = pd.read_csv("https://raw.githubusercontent.com/deepsuthapa/AniGen1/refs/heads/master/AnimeReccSystem/AnimeReccSystem/rating.csv").drop_duplicates()
    final = pd.merge(anime, ratings, on="anime_id", suffixes=[None, "_user"])
    final = final.rename(columns={"rating_user": "user_rating"})
    return anime, final


# Clean text function
def text_cleaning(text):
    text = re.sub(r'&quot;', '', text)
    text = re.sub(r'.hack//', '', text)
    text = re.sub(r'&#039;', '', text)
    text = re.sub(r'A&#039;s', '', text)
    text = re.sub(r'I&#039;', 'I\'', text)
    text = re.sub(r'&amp;', 'and', text)
    return text


# Recommendation Function
def give_recommendation(title, tfv, sig, rec_indices, anime):
    idx = rec_indices[title]  # Get index corresponding to title
    sig_score = list(enumerate(sig[idx]))  # Get pairwise similarity scores
    sig_score = sorted(sig_score, key=lambda x: x[1], reverse=True)[1:11]  # Top 10
    anime_indices = [i[0] for i in sig_score]

    rec_dic = {
        "No": range(1, 11),
        "Anime Name": anime["name"].iloc[anime_indices].values,
        "Rating": anime["rating"].iloc[anime_indices].values
    }

    dataframe = pd.DataFrame(data=rec_dic)
    dataframe.set_index("No", inplace=True)
    return dataframe


# Scrape images from MyAnimeList
def scrape_images(search_query):
    url = f"https://myanimelist.net/anime.php?q={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Assuming image URLs are in 'img' tags with the class 'lazyload' (actual class might vary)
    image_elements = soup.find_all('img', class_='lazyload')
    image_urls = [img['data-src'] for img in image_elements if 'data-src' in img.attrs]

    return image_urls


# Where to Watch Feature - Fetches streaming platform links
def fetch_streaming_links(anime_name):
    # Replace this logic with scraping or API calls to get real streaming links
    streaming_platforms = {
        "Crunchyroll": f"https://www.crunchyroll.com/search?&q={anime_name}",
        "Funimation": f"https://www.funimation.com/search/?q={anime_name}",
        "HiAnime": f"https://www.hianime.to/search?keyword={anime_name}",
    }
    return streaming_platforms


# Main Streamlit App
def main():
    # Set the background image (provide the absolute path to your local image)
    # set_background(
    #     r"all_anime_in_one.jpg")  # Use raw string for Windows path

    # Custom title with larger font and different style
    st.markdown(
        """
        <h1 style='text-align: center; font-family: "Comic Sans MS"; font-size: 120px; color: #FFD700;'>
            Know Your Anime!!
        </h1>
        """,
        unsafe_allow_html=True
    )

    # Load data
    anime, final = load_data()
    final["name"] = final["name"].apply(text_cleaning)

    # Prepare for recommendations
    rec_data = final.drop_duplicates(subset="name", keep="first").reset_index(drop=True)
    tfv = TfidfVectorizer(min_df=3, max_features=None, strip_accents="unicode", analyzer="word",
                          token_pattern=r"\w{1,}", ngram_range=(1, 3), stop_words="english")

    genres = rec_data["genre"].str.split(", | , | ,").astype(str)
    tfv_matrix = tfv.fit_transform(genres)
    sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
    rec_indices = pd.Series(rec_data.index, index=rec_data["name"]).drop_duplicates()

    # User input for recommendations
    anime_name = st.selectbox("Select an Anime:", anime["name"].unique())

    if st.button("Get Recommendations"):
        if anime_name in rec_indices.index:
            recommendations = give_recommendation(anime_name, tfv, sig, rec_indices, anime)
            st.subheader(f"Recommendations for '{anime_name}' viewers:")
            st.dataframe(recommendations.style.set_properties(
                **{"background-color": "#2a9d8f", "color": "white", "border": "1.5px solid black"}))
        else:
            st.error(f"Anime '{anime_name}' not found in the dataset.")

    # Anime Search by Genre
    st.subheader("Anime Search by Genre")
    with st.container():
        st.markdown(
            """
            <div style="background-color: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 5px;">
                <p style="color: white;">Select Genre(s):</p>
            </div>
            """, unsafe_allow_html=True
        )
        all_genres = set()
        for genres in anime['genre'].dropna():
            all_genres.update(genre.strip() for genre in genres.split(','))
        selected_genres = st.multiselect("Select Genre(s)", sorted(all_genres))
        if selected_genres:
            filtered_data = anime[anime['genre'].apply(lambda x: all(genre in x for genre in selected_genres) if pd.notna(x) else False)]
            if not filtered_data.empty:
                st.write(f"### Results ({len(filtered_data)})")
                for _, row in filtered_data.iterrows():
                    anime_type = row.get('type', 'N/A')  # Safely get 'type' or return 'N/A'
                    episodes = row.get('episodes', 'N/A')  # Safely get 'episodes' or return 'N/A'
                    st.write(f"**{row['name']}** - {anime_type} - {episodes} episodes - Rating: {row['rating']}")
                    st.write(f"Genres: {row['genre']}")
                    st.write("---")
            else:
                st.write("No results found for the selected genres.")
        else:
            st.write("Please select at least one genre.")

    # Genre WordCloud
    st.subheader("Genre WordCloud")
    with st.container():
        st.markdown(
            """
            <div style="background-color: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 5px;">
                <p style="color: white;">Genre WordCloud:</p>
            </div>
            """, unsafe_allow_html=True
        )
        wordcloud = WordCloud(width=800, height=250, background_color='black', colormap='viridis', collocations=False).generate(" ".join(anime['genre'].dropna()))
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt)

    # Where to Watch Section
    st.subheader("Where to Watch Anime")
    with st.container():
        st.markdown(
            """
            <div style="background-color: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 5px;">
                <p style="color: white;">Enter the anime name to find where to watch it:</p>
            </div>
            """, unsafe_allow_html=True
        )
        where_to_watch_query = st.text_input("Enter the anime name to find where to watch it:")

        if st.button("Search Where to Watch"):
            if where_to_watch_query:
                where_to_watch_query = where_to_watch_query.replace(' ', '+')
                streaming_links = fetch_streaming_links(where_to_watch_query)
                if streaming_links:
                    st.write(f"Streaming platforms for '{where_to_watch_query}':")
                    for platform, link in streaming_links.items():
                        st.markdown(f"- [{platform}]({link})")
                else:
                    st.write("No streaming links found.")
            else:
                st.error("Please enter an anime name to search for streaming links.")

    # Image Scraper Section
    st.subheader("Search Anime Images")
    with st.container():
        st.markdown(
            """
            <div style="background-color: rgba(0, 0, 0, 0.7); padding: 20px; border-radius: 5px;">
                <p style="color: white;">Enter the anime name to search images:</p>
            </div>
            """, unsafe_allow_html=True
        )
        search_query = st.text_input("Enter the anime name to search images:")
        if st.button("Search Images"):
            if search_query:
                image_urls = scrape_images(search_query)
                if image_urls:
                    st.write(f"Found {len(image_urls)} images for '{search_query}':")
                    for url in image_urls:
                        st.image(url, use_column_width=True)
                else:
                    st.write("No images found.")
            else:
                st.error("Please enter an anime name to search for images.")


if __name__ == "__main__":
    main()

import numpy as np
import pandas as pd
import streamlit as st

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
    st.title("Anime Recommendation & Image Scraper")


    # Where to Watch Section
    st.subheader("Where to Watch Anime")
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


if __name__ == "__main__":
    main()
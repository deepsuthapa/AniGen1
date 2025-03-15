import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Entry, Button

def search_and_scrape(search_query):
    """
    Fetches image URLs based on a user-provided search query.

    Args:
        search_query (str): The user's search term.
    """

    url = f"https://myanimelist.net/anime.php?q={search_query}"
    image_urls = scrape_images(url)

    if image_urls:
        print(f"Found {len(image_urls)} images:")
        for url in image_urls:
            print(url)
    else:
        print("No images found.")

def scrape_images(url):
    """
    Scrapes image URLs from a website.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        list: A list of image URLs found on the website.
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Assuming image URLs are in 'img' tags with the class 'anime-image'
    image_elements = soup.find_all('img', class_='anime-image')

    image_urls = [img['src'] for img in image_elements]

    return image_urls

# Create a GUI window
root = Tk()
root.title("Image Scraper")

# Create a label and entry box for search query
search_label = Label(root, text="Enter your search query:")
search_label.pack()

search_entry = Entry(root)
search_entry.pack()

# Define a function to handle button click
def button_click():
    search_term = search_entry.get()
    search_and_scrape(search_term)

# Create a button to trigger the search
search_button = Button(root, text="Search", command=button_click)
search_button.pack()

# Run the main event loop
root.mainloop()
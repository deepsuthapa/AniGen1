<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MangaDex Clone</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        .manga-cover {
            width: 150px;
            height: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="my-4">MangaDex Clone</h1>
        <div id="latest-updates" class="row"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script>
        const CORS_PROXY = "https://cors-anywhere.herokuapp.com/";
        const API_URL = "https://api.mangadex.org/manga";
        const COVER_URL = "https://uploads.mangadex.org/covers";

        async function getLatestManga(limit = 10, searchQuery = null) {
            const params = { limit, 'order[updatedAt]': 'desc' };
            if (searchQuery) {
                params.title = searchQuery;
            }
            try {
                const response = await axios.get(CORS_PROXY + API_URL, { params });
                return response.data.data;
            } catch (error) {
                console.error('Error fetching latest manga:', error);
                return [];
            }
        }

        async function getCoverImage(manga) {
            try {
                const coverArt = manga.relationships.find(rel => rel.type === 'cover_art');
                if (coverArt) {
                    const coverId = coverArt.id;
                    const coverRes = await axios.get(CORS_PROXY + `https://api.mangadex.org/cover/${coverId}`);
                    const coverFilename = coverRes.data.data.attributes.fileName;
                    return `${COVER_URL}/${manga.id}/${coverFilename}`;
                }
                return "https://via.placeholder.com/150";
            } catch (error) {
                console.error('Error fetching cover image:', error);
                return "https://via.placeholder.com/150";
            }
        }

        async function displayLatestManga() {
            const latestManga = await getLatestManga();
            const updatesContainer = document.getElementById('latest-updates');
            updatesContainer.innerHTML = '';

            for (const manga of latestManga) {
                const mangaId = manga.id;
                const title = manga.attributes.title.en || "Unknown Title";
                const desc = manga.attributes.description.en || "No description available.";
                const coverUrl = await getCoverImage(manga);

                const mangaCard = document.createElement('div');
                mangaCard.className = 'col-md-6 mb-4';
                mangaCard.innerHTML = `
                    <div class="card">
                        <img src="${coverUrl}" class="card-img-top manga-cover" alt="${title}">
                        <div class="card-body">
                            <h5 class="card-title">${title}</h5>
                            <p class="card-text">${desc.substring(0, 200)}...</p>
                            <a href="https://mangadex.org/title/${mangaId}" class="btn btn-primary" target="_blank">Read</a>
                        </div>
                    </div>
                `;
                updatesContainer.appendChild(mangaCard);
            }
        }

        document.addEventListener('DOMContentLoaded', displayLatestManga);
    </script>
</body>
</html>
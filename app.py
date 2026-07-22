import os
import pickle
import pandas as pd
import requests
import streamlit as st

# 1. MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")

# 2. AUTO-DOWNLOAD SIMILARITY MODEL IF NOT FOUND
SIMILARITY_URL = "https://github.com/parthadutta1/CineMatch/releases/download/v1.0/similarity.pkl"
SIMILARITY_FILE = "similarity.pkl"

if not os.path.exists(SIMILARITY_FILE):
    st.info("Downloading similarity model file for first-time setup... This may take a few seconds.")
    response = requests.get(SIMILARITY_URL, stream=True)
    with open(SIMILARITY_FILE, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

# Your TMDB API Key
TMDB_API_KEY = "a39539f0a4710c607a061029d4a71bb1"


# Function to fetch poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
    except Exception:
        pass

    return "https://placehold.co/500x750/1e1e1e/ffffff?text=No+Poster"


# Function to get recommendations
def recommend(movie_title):
    index = movies[movies["title"] == movie_title].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1]
    )

    recommended_names = []
    recommended_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_names.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_names, recommended_posters


st.title("🎬 CineMatch: Movie Recommender System")
st.write("Select a movie you like to get personalized recommendations!")

# Load pickle files
try:
    movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
    similarity = pickle.load(open(SIMILARITY_FILE, "rb"))
    movies = pd.DataFrame(movies_dict)

    selected_movie = st.selectbox(
        "Type or select a movie from the list:", movies["title"].values
    )

    if st.button("Get Recommendations"):
        with st.spinner("Finding similar movies..."):
            names, posters = recommend(selected_movie)

        cols = st.columns(5)
        for col, name, poster in zip(cols, names, posters):
            with col:
                st.subheader(name)
                st.image(poster, width="stretch")

except FileNotFoundError:
    st.error(
        "Pickle files not found! Please run 'python build_model.py' first."
    )
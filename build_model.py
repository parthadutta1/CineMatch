import ast
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("1. Loading Datasets...")
movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

# Merge datasets based on movie title
movies = movies.merge(credits, on="title")

# Pick useful columns for content matching
movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]
movies.dropna(inplace=True)


# Helper functions to extract names from JSON strings
def convert(text):
    return [item["name"] for item in ast.literal_eval(text)]


def convert_cast(text):
    # Get top 3 actors
    return [item["name"] for item in ast.literal_eval(text)[:3]]


def fetch_director(text):
    # Get Director name only
    for item in ast.literal_eval(text):
        if item["job"] == "Director":
            return [item["name"]]
    return []


print("2. Cleaning Data...")
movies["genres"] = movies["genres"].apply(convert)
movies["keywords"] = movies["keywords"].apply(convert)
movies["cast"] = movies["cast"].apply(convert_cast)
movies["crew"] = movies["crew"].apply(fetch_director)
movies["overview"] = movies["overview"].apply(lambda x: x.split())

# Remove spaces inside names (e.g., "Johnny Depp" -> "JohnnyDepp") so words don't mix up
for col in ["genres", "keywords", "cast", "crew"]:
    movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])

# Combine all descriptions/tags into one big list of words per movie
movies["tags"] = (
    movies["overview"]
    + movies["genres"]
    + movies["keywords"]
    + movies["cast"]
    + movies["crew"]
)

# Create simplified dataframe
new_df = movies[["movie_id", "title", "tags"]].copy()
new_df["tags"] = new_df["tags"].apply(lambda x: " ".join(x).lower())

print("3. Calculating Similarities (Vectorization)...")
# Convert text tags to 5000 numbers/vectors
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(new_df["tags"]).toarray()

# Calculate Cosine Similarity (angle distance between every pair of movies)
similarity = cosine_similarity(vectors)

print("4. Exporting Pickle Files...")
# Save processed movies dictionary and similarity matrix
pickle.dump(new_df.to_dict(), open("movie_dict.pkl", "wb"))
pickle.dump(similarity, open("similarity.pkl", "wb"))

print("✅ Model build complete! Generated 'movie_dict.pkl' and 'similarity.pkl'.")
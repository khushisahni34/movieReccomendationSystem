import pickle
import streamlit as st
import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load Data
movies = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Ensure movies is a dataframe
if isinstance(movies, dict):
    movies = pd.DataFrame(movies)

# TMDB API Key
API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# Fetch Poster Function
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

# Fetch Genres Function (for Explainability)
def fetch_genre(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    data = requests.get(url).json()
    genres = data.get('genres', [])
    genre_names = ", ".join([genre['name'] for genre in genres])
    return genre_names if genre_names else "No Genre Info"

# Recommend Function
def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found. Please choose a valid movie from the list.")
        return [], [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_genres = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_genres.append(fetch_genre(movie_id))

    return recommended_movie_names, recommended_movie_posters, recommended_movie_genres

# Sentiment Analysis (Bonus Feature)
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    return score['compound']

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommendation System with Explainability & Sentiment Analysis')

movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendations'):
    names, posters, genres = recommend(selected_movie)
    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i])
                st.subheader(names[i])
                st.caption(f"Genre: {genres[i]}")

# Optional: Sentiment Analysis Demo
st.markdown("---")
st.header("📝 Movie Review Sentiment Analyzer")
user_review = st.text_area("Enter any review text here:")

if st.button("Analyze Sentiment"):
    score = analyze_sentiment(user_review)
    if score >= 0.05:
        st.success(f"Positive Sentiment: {score}")
    elif score <= -0.05:
        st.error(f"Negative Sentiment: {score}")
    else:
        st.warning(f"Neutral Sentiment: {score}")

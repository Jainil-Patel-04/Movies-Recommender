import pickle
import streamlit as st
import requests
import re 

def format_list_items(items):
    formatted = []
    for item in items:
        # Add space between camelCase words
        formatted_item = re.sub(r'([a-z])([A-Z])', r'\1 \2', item)
        formatted.append(formatted_item)
    return ", ".join(formatted)

def format_overview(overview_list):
    return " ".join(overview_list).replace(" - ", "-")  # Fix hyphen spacing

def fetch_poster_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={st.secrets['omdb']['api_key']}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        # Improved poster handling
        poster = data.get("Poster")
        if not poster or poster == "N/A":
            return "https://placehold.co/500x750?text=Poster+Not+Available"
        return poster
    except Exception as e:
        print("OMDb Error:", e)
        return "https://via.placeholder.com/500x750.png?text=Error+Loading+Poster"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].title
        recommended_movie_posters.append(fetch_poster_omdb(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie)
    st.session_state.recommendations = list(zip(names, posters))

if 'recommendations' in st.session_state:
    st.subheader("Recommended Movies")
    cols = st.columns(5)
    for i, (name, poster) in enumerate(st.session_state.recommendations):
        with cols[i]:
            st.text(name)
            st.image(poster)
            if st.button("Details", key=f"btn_{i}"):
                st.session_state.selected_movie = name

if 'selected_movie' in st.session_state:
    movie = movies[movies['title'] == st.session_state.selected_movie].iloc[0]
    st.subheader("Movie Details")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(fetch_poster_omdb(movie['title']))
    
    with col2:
        st.markdown(f"**Title:** {movie['title']}")
        
        # Format Director information
        directors = format_list_items(movie['crew']) if isinstance(movie['crew'], list) else movie['crew']
        st.markdown(f"**Director:** {directors}")
        
        # Format Cast information
        cast = format_list_items(movie['cast'][:5]) if isinstance(movie['cast'], list) else movie['cast']
        st.markdown(f"**Cast:** {cast}")
        
        # Added Genres display
        genres = format_list_items(movie['genres']) if isinstance(movie['genres'], list) else movie['genres']
        st.markdown(f"**Genres:** {genres}")
        
        # Format Overview
        overview = format_overview(movie['overview']) if isinstance(movie['overview'], list) else movie['overview']
        st.markdown(f"**Overview:** {overview}")
    
    if st.button("Close Details"):
        del st.session_state.selected_movie
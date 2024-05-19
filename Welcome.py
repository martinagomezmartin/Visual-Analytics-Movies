import streamlit as st
from PIL import Image


st.set_page_config(
page_title="Welcome",
page_icon="👋",
layout="wide",
initial_sidebar_state="expanded")

st.sidebar.header("Navigate through the different tabs to learn about all about movies")


#The title
st.title("🍿🎬 Movies Exploration ")

#The subheader
st.subheader("Are you interested in the movie industry? Are you a film fanatic? ")

#The text
st.write("You have come to right place! ")
st.markdown("Get ready for a cinematic time-travel! We're about to dive into the ride of how popular movies have changed over the years and we are going to investigate what makes a film succeed breaking down the trends that make movies a hit.\n \n In this study we are going to be using the IMDb Movies Dataset which contains observations of 10k+ movies like `title`, `budget`, `revenue`, `cast`, `director`, `tagline`, `keywords`, `genres`, `release date`, `runtime` etc. we will be able to get some insights on the movie industry and the factors that are influencial in making a successful movie.") 

st.image('IMDB.png', use_column_width=True)
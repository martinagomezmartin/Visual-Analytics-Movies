import pandas as pd
import streamlit as st
import re

def fill_missing_value(data):
    data['production_companies'].fillna(value = 'Other', inplace=True)
    data['keywords'].fillna(value = 'uknown', inplace=True)
    data['director'].fillna(value = 'Other', inplace=True)

    return data

@st.cache_data
def load_data(drop_rows = True):
    df = pd.read_csv("tmdb_movies_data.csv")

    df.drop_duplicates(inplace = True)

    df.drop(['budget_adj','revenue_adj','imdb_id','homepage'],axis =1,inplace = True)
    df = df[df['budget'] != 0].copy()
    df = df[df['revenue'] != 0].copy()
    #GENRE PROCESSING
    # Replace NaN values in 'genres' column with 'Unknown'
    df['genres'].fillna('Unknown', inplace=True)

    # Count the occurrences of each genre
    genre_counts = df['genres'].str.split('|', expand=True).stack().value_counts()

    # Select the top 15 genres
    top_genres = genre_counts.head(15).index.tolist()

    # Create one-hot encoding for the top genres and 'genre_other'
    for genre in top_genres:
        df[f'genre_{genre.lower()}'] = df['genres'].apply(lambda x: 1 if genre in x else 0)

    # Create 'genre_other'
    df['genre_other'] = df['genres'].apply(lambda x: 1 if all(genre not in x for genre in top_genres) else 0)

        # EXTRACTING MONTH AND YEAR
    df['release_date'] = pd.to_datetime(df['release_date'])

    # Extract month and year
    if drop_rows:
        df['release_month'] = df['release_date'].dt.month
        df['release_year'] = df['release_date'].dt.year

    # ADD PROFIT
    df['profit']= df['revenue'] - df ['budget'] 
    # SPLITING MULTIVALUED COLUMNS
    df['keywords'] = df['keywords'].str.replace('|', ' ')
    df['cast'] = df['cast'].astype(str)
    df['cast']= df['cast'].apply(lambda x: re.sub( r"([A-Z])", r" \1", x))
    df['cast'] = df['cast'].apply(lambda x: x.split("|"))
    df = df[df['cast'].apply(lambda x: 'nan' not in x)]

    df = fill_missing_value(df)
    df = add_actor_rel(df)

    return df

def add_actor_rel(df):
    new_df = df.copy()
    # Split the actors column
    df_actors = new_df.explode('cast')
    df_actors['actor'] = df_actors['cast'].apply(lambda actor: actor.strip())

    actor_popularity = df_actors.groupby('actor')['popularity'].sum().reset_index()
    actor_revenue = df_actors.groupby('actor')['revenue'].sum().reset_index()
    actor_ratings = df_actors.groupby('actor')['vote_average'].sum().reset_index()

    top_actors_popularity = actor_popularity.sort_values(by='popularity', ascending=False).head(10)
    top_actors_revenue = actor_revenue.sort_values(by='revenue', ascending=False).head(10)
    top_actors_ratings = actor_ratings.sort_values(by='vote_average', ascending=False).head(10)
    actors_set = set(top_actors_popularity['actor']).union(top_actors_revenue['actor']).union(top_actors_ratings['actor'])
    top_actors = list(actors_set)

    # Create a new column 'famous_director' and set values based on whether the director is in the list
    df['famous_actors'] = df['cast'].apply(lambda x: sum(actor.strip() in top_actors for actor in x))
    return df 

def add_director_rel(df):
    new_df = df.copy()
    # Split the directors column
    new_df['director'] = new_df['director'].str.split('|')

    # Explode the DataFrame to create separate rows for each director
    df_directors = new_df.explode('director')

    director_popularity = df_directors.groupby('director')['popularity'].sum().reset_index()
    director_revenue = df_directors.groupby('director')['revenue'].sum().reset_index()
    director_ratings = df_directors.groupby('director')['vote_average'].sum().reset_index()


    top_directors_popularity = director_popularity.sort_values(by='popularity', ascending=False).head(10)
    top_directors_revenue = director_revenue.sort_values(by='revenue', ascending=False).head(10)
    top_directors_ratings = director_ratings.sort_values(by='vote_average', ascending=False).head(10)
    
    directors_set = set(top_directors_popularity['director']).union(top_directors_revenue['director']).union(top_directors_ratings['director'])
    top_directors = list(directors_set)

    # Create a new column 'famous_director' and set values based on whether the director is in the list
    df['famous_director'] = df['director'].apply(lambda x: 1 if x in top_directors else 0)
    return df

def add_production_companies(df):
    production_companies = df.copy()
    production_companies=production_companies['production_companies'].str.split('|', expand=True).stack().reset_index(level=1, drop=True).rename('production_companies')
    df_production_companies = df.drop('production_companies', axis=1).join(production_companies)

    df_production_companies = df_production_companies.groupby(['production_companies'])['revenue'].sum().reset_index()
    companies_popularity = df_production_companies.sort_values(by='revenue', ascending=False)
    companies_popularity = companies_popularity.head(10)

    # Getting the top 10 production companies
    top_production_companies = production_companies.head(10)
    list_production_companies = set(top_production_companies.index).union(set(companies_popularity['production_companies']))
    top_prod_companies = list(list_production_companies)

    # Create a new column 'famous_director' and set values based on whether the director is in the list
    df['famous_company'] = df['production_companies'].apply(lambda x: 1 if x in top_prod_companies else 0)
    return df
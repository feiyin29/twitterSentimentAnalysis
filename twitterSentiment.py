# import Library
import streamlit as st
import streamlit.components.v1 as components
from cleantext import clean
import numpy as np
import pymongo
from pymongo import MongoClient
import json
import tweepy as tw
from pprint import pprint
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import re
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

# Back-end

# Keys and Access Tokens from twiter api
consumer_key = '77UdiVpfBQpFZDvxuPlgvMFHs'
consumer_secret = 'AvycXqpzW6eMv0sjZA6nkLGwqOh4Gh0WRCId0JAKVnABgxP3gb'
access_token = '1531544153275785216-ei4xlrXO8sKVb3QXbkE3Mm12o6W6Jx'
access_token_secret = 'qpA5x82cFKlTnOCqSwwgdQQtzjpRECwkYYV4Ki4NHxAOv'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

#Search a word from twitter
def search_tweets(language, hashtag, number):

    # Define the search term and the date_since date as variables
    search_words = hashtag
    new_search = search_words + " -filter:retweets"  # Do not get retweet of tweets
    # Collect tweets
    tweets = tw.Cursor(api.search_tweets, q=new_search,
                       lang=language).items(number)

    users_locs = [[tweet.text] for tweet in tweets]

    # To Dataframe
    tweet_df = pd.DataFrame(data=users_locs, columns=['text'])

    # return Dataframe
    return tweet_df

#default dataframe
df = search_tweets('en', 'blackpink', 10)

# clean data
# create a function to clean the tweets
def cleanTxt(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)  # remove @
    text = re.sub(r'#', '', text)  # Remove the '#' symbol
    text = re.sub(r'RT[\s]+', '', text)  # remove RT
    text = re.sub(r'https?:\/\/\S+', '', text)  # remove hyper link
    text = clean(text, no_emoji=True) # remove emoji

    return text


# Cleaning the text
df['text'] = df['text'].apply(cleanTxt)

# Connect MongoDB
mongod_connect = "mongodb+srv://bigdata_tweets:bigdata@cluster0.hifh0z9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongod_connect)
db = client.bigdata_tweets  # use or create a database named demo

# use or create a collection named tweet_collection
tweet_collection = db.tweets_sentiment

def query(df):
    # Cleaning the text
    df['text'] = df['text'].apply(cleanTxt)

    #create and write json file
    with open('df.json', 'w') as f:
        f.write(df.to_json())

    #Load json file for insert to DB
    with open('df.json') as file:
        file_data = json.load(file)
    
    #delete data in DB
    tweet_collection.delete_many({})

    #insert data in json file to DB
    tweet_collection.insert_one(file_data)

# call function query to query data
query(df)

# create  a function to get the subjectivity
def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

# create a function to get the polarity -> negative positive
def getPolarity(text):
    return TextBlob(text).sentiment.polarity

# create two new column
df['Subjectivity'] = df['text'].apply(getSubjectivity)
df['Polarity'] = df['text'].apply(getPolarity)

# check polarity state
def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

# call getAnalysis function to store in Dataframe
df['Analysis'] = df['Polarity'].apply(getAnalysis)

# wordClound Generate and make it circle
def wordCloundIMG(df):
  text = ' '.join([twts for twts in df['text']])

  x, y = np.ogrid[:300, :300]

  mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
  mask = 255 * mask.astype(int)

  wc = WordCloud(background_color="white", repeat=True, mask=mask)
  wc.generate(text)

  fig, ax = plt.subplots()
  ax.imshow(wc, interpolation='bilinear')
  ax.axis("off")
  st.pyplot(fig)

# visualize to bar chart
def showValueCounts():
# show the value counts
  df['Analysis'].value_counts()

# plot and visualize the count
  fig,ax = plt.subplots()
  df['Analysis'].value_counts().plot(kind='bar')
  st.pyplot(fig)

# front-end
# set page title and layout
st.set_page_config(
     page_title='Word Cloud',
     layout="wide",
     initial_sidebar_state="expanded",
)

def main():
    body()
    return None 

def body():
    with st.container():
        # set header title
        header_title = '<p style="font-family:sans-serif; font-size: 52px;">Word Cloud</p>'
        st.markdown(header_title, unsafe_allow_html=True)
        text = ""

        # example word 
        col1, col2, col3, col4, col5, col6= st.columns((0.3, 0.24, 0.27, 0.3, 0.24, 1))   
        with col1:
            eaxm = '<p style=" font-weight: 600;font-size: 24px; padding-top: 23px;">example word :</p>'
            st.markdown(eaxm, unsafe_allow_html=True)
        with col2:
            if(st.button('Netflix')):
                text = "Netflix"
        with col3:
            if(st.button('apec2022')):
                text = "apec2022"
        with col4:
            if(st.button('#RIPtwitter')):
                text = "#RIPtwitter"
        with col5:
            if(st.button('nct127')):
                text = "nct127"
        with col6:
            if(st.button('#UnderTheQueensUmbrellaEp12')):
                text = "#UnderTheQueensUmbrellaEp12"

        col7, col8, col9, col10, col11, col12 = st.columns((0.3, 0.39, 0.36, 0.26, 0.4,1))
        with col7:
            if(st.button('covid-19')):
                text = "covid-19"            
        with col8:
            if(st.button('Christmas2022')):
                text = "Christmas2022"
        with col9:
            if(st.button('newyear2023')):
                text = "newyear2023"
        with col10:
            if(st.button('lgbtq+')):
                text = "lgbtq+"            
        with col11:
            if(st.button('CHAEUNWOO')):
                text = "CHAEUNWOO"
        
        # search bar and button
        _, search1, search2, _ = st.columns((0.5,2,0.5,0.5))
        with search1:
            name = st.text_input('', text,placeholder="Search")
        with search2:
            if(st.button('Generate')):
                result = name.title()
            df = search_tweets('en', name, 100)
            query(df)
       
        # Show wordcloud image and bar chart
        _, pic, _ = st.columns((1,2,1))
        with pic:
            wordCloundIMG(df) 
            titleGraph = '<p style="font-family:sans-serif; font-size: 30px; padding-top: 30px;">Graph Analysis Sentiment</p>'
            st.markdown(titleGraph, unsafe_allow_html=True)

            descGraph = '<p style="font-family:sans-serif; font-size: 18px;">This chart shows the computed negative, neutral, and positive analysis.</p>'
            st.markdown(descGraph, unsafe_allow_html=True)
            showValueCounts() 
            
    return None

# call main front-end
if __name__ == '__main__':
    main()

# css     
m = st.markdown("""
<style>
    /* set background */
    [data-testid="stAppViewContainer"]  {
        background-color: #EEFAFF;
        background-image: url("https://cdn.discordapp.com/attachments/1032648545511161897/1044582208700158045/bg_big.jpg");
        background-size: cover
    }
    /* set button state */
    div.stButton > button:first-child {
        border-radius: 53px;
        color:#ffffff;
        padding: 10px 32px;
        margin-top: 25px;
    }
    div.stButton > button:hover {
        border-radius: 53px;
        color:#000000;
        border-color: #000000;
        padding: 10px 32px;
        margin-top: 25px;
        box-shadow: 0px 0px 0px 0px rgb(0,0,0);
    }
    div.stButton > button:focus {
        border-radius: 53px;
        color:#252525;
        border-color: #252525;
        border-width: 3px;
        padding: 10px 32px;
        box-shadow: 0px 0px 0px 0px rgb(0,0,0);
    }
    /* set style search bar */
    [data-baseweb="input"] {
        border-radius: 53px;
        border-style: solid;
        border-width: 1.5px;
    }
</style>""", unsafe_allow_html=True)    

# set button color
components.html(
    """
<script>
const elements = window.parent.document.querySelectorAll('.stButton button')
elements[0].style.backgroundColor = '#F2DD05'
elements[1].style.backgroundColor = '#0894B8'
elements[2].style.backgroundColor = '#EC8C87'
elements[3].style.backgroundColor = '#3FB971'
elements[4].style.backgroundColor = '#E9713F'
elements[5].style.backgroundColor = '#EC8C87'
elements[6].style.backgroundColor = '#3FB971'
elements[7].style.backgroundColor = '#E9713F'
elements[8].style.backgroundColor = '#F2DD05'
elements[9].style.backgroundColor = '#0894B8'
elements[10].style.backgroundColor = '#0949B6'

</script>
""",
    height=0,
    width=0,
)
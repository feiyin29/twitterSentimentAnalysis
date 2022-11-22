# import base64
import streamlit as st
import streamlit.components.v1 as components

# st.header("Hello World 👏")

# st.write("This is my first app")

from cleantext import clean
import numpy as np

import pymongo
from pymongo import MongoClient
import json
import tweepy as tw
# import twitter
from pprint import pprint
import pandas as pd
# word cloud
from textblob import TextBlob
from wordcloud import WordCloud
import re
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')


# Keys and Access Tokens
consumer_key = '77UdiVpfBQpFZDvxuPlgvMFHs'
consumer_secret = 'AvycXqpzW6eMv0sjZA6nkLGwqOh4Gh0WRCId0JAKVnABgxP3gb'
access_token = '1531544153275785216-ei4xlrXO8sKVb3QXbkE3Mm12o6W6Jx'
access_token_secret = 'qpA5x82cFKlTnOCqSwwgdQQtzjpRECwkYYV4Ki4NHxAOv'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)


def search_tweets(language, hashtag, number):

    # Define the search term and the date_since date as variables
    search_words = hashtag
    #date_since = date
    new_search = search_words + " -filter:retweets"  # Do not get retweet of tweets

    # Collect tweets
    tweets = tw.Cursor(api.search_tweets, q=new_search,
                       lang=language).items(number)

    users_locs = [[tweet.text] for tweet in tweets]

    # To Dataframe
    tweet_df = pd.DataFrame(data=users_locs, columns=['text'])

    # return Dataframe
    return tweet_df


df = search_tweets('en', 'blackpink', 10)

# df.sample(10)

# clean data

# create a function to clean the tweets


def cleanTxt(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)  # remove @
    text = re.sub(r'#', '', text)  # Remove the '#' symbol
    text = re.sub(r'RT[\s]+', '', text)  # remove RT
    text = re.sub(r'https?:\/\/\S+', '', text)  # remove hyper link
    text = clean(text, no_emoji=True)

    return text


# Cleaning the text
df['text'] = df['text'].apply(cleanTxt)

# Show the cleaned text
# df

# Connect MongoDB
mongod_connect = "mongodb+srv://bigdata_tweets:bigdata@cluster0.hifh0z9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongod_connect)
db = client.bigdata_tweets  # use or create a database named demo

# use or create a collection named tweet_collection
tweet_collection = db.tweets_sentiment

def query(df):
    # Cleaning the text
    df['text'] = df['text'].apply(cleanTxt)

    with open('df.json', 'w') as f:
        f.write(df.to_json())

    with open('df.json') as file:
        file_data = json.load(file)


    tweet_collection.delete_many({})
    tweet_collection.insert_one(file_data)

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

# show the new dataframe with yhe new column
# df

def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


df['Analysis'] = df['Polarity'].apply(getAnalysis)

# show the dataframe
# df

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

def showValueCounts():
# show the value counts
  data = df['Analysis'].value_counts()

# plot and visualize the count
  fig,ax = plt.subplots()
#   fig.title('sentiment Analysis')
#   fig.xlabel('Sentiment')
#   fig.ylabel('Counts')
  df['Analysis'].value_counts().plot(kind='bar')
#   plt.show()
  st.pyplot(fig)
  
# queryDB(tweet_collection)
# wordCloundIMG()

  # -------------------- UI ver2 ------------------------
st.set_page_config(
     page_icon="🧊",
     page_title='Word Cloud',
     layout="wide",
     initial_sidebar_state="expanded",
)

def main():
    cs_body()
    return None 

def cs_body():
    with st.container():
        # header_title = '<p style="font-family:sans-serif; color:Green; font-size: 42px;">Word Cloud</p>'
        header_title = '<p style="font-family:sans-serif; font-size: 52px;">Word Cloud</p>'
        st.markdown(header_title, unsafe_allow_html=True)
        text = ""
        # example
        col1, col2, col3, col4, col5, col6= st.columns((0.3, 0.24, 0.27, 0.3, 0.24, 1))   
        with col1:
            eaxm = '<p style=" font-weight: 600;font-size: 24px; padding-top: 23px;">example :</p>'
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
        
        # Search + Picture
        # left, right = st.columns((2,1))
        # with left:
        #     title = st.text_input('', '',placeholder="Search")
        #     df = search_tweets('en', title, 100)
        # with right:
        #     wordCloundIMG(df)
                
            
        # # Search box   
        # search1, search2, search3 = st.columns((0.5,2,0.5))
        # with search2:
        #     title = st.text_input('', 'Search')

        # df = search_tweets('en', title, 100)

        # # Gen pic
        # emp1, pic, emp2 = st.columns((1,2,1))
        # with pic:
        #     wordCloundIMG(df)
        search1, search2, search3, search4 = st.columns((0.5,2,0.5,0.5))
        with search2:
            name = st.text_input('', text,placeholder="Search")
        with search3:
            if(st.button('Generate')):
                result = name.title()
            df = search_tweets('en', name, 100)
            query(df)
       
        # Gen pic
        emp1, pic, emp2 = st.columns((1,2,1))
        with pic:
            wordCloundIMG(df) 
            titleGraph = '<p style="font-family:sans-serif; font-size: 30px; padding-top: 30px;">Graph Analysis Sentiment</p>'
            st.markdown(titleGraph, unsafe_allow_html=True)

            descGraph = '<p style="font-family:sans-serif; font-size: 18px;">This chart shows the computed negative, neutral, and positive analysis.</p>'
            st.markdown(descGraph, unsafe_allow_html=True)
            showValueCounts() 
            
        # form = st.form(key='my-form')
        # name = form.text_input('', '',placeholder="Search")
        # submit = form.form_submit_button('Submit')

        # if submit:
        #     st.write(f'hello {name}')
            
    # def dfClick():
    #     df = search_tweets('en', title, 100)
    #     wordCloundIMG(df)

            
    return None

if __name__ == '__main__':
    main()


    
# @st.experimental_memo
# def get_img_as_base64(file):
#     with open(file, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# img = get_img_as_base64("bird.png")

        

m = st.markdown("""
<style>
    [data-testid="stAppViewContainer"]  {
        background-color: #EEFAFF;
        background-image: url("https://cdn.discordapp.com/attachments/1032648545511161897/1044582208700158045/bg_big.jpg");
        background-size: cover
    }
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
    div.stButton > button:active {
        border-radius: 53px;
        color:#000000;
        border-color: #000000;
        padding: 10px 32px;
        box-shadow: 0px 0px 0px 0px rgb(0,0,0);
    }
    div.stButton > button:focus {
        border-radius: 53px;
        color:#000000;
        border-color: #252525;
        border-width: 5px;
        padding: 10px 32px;
        box-shadow: 0px 0px 0px 0px rgb(0,0,0);
    }
    div.stButton > button:visited {
        border-radius: 53px;
        color:#000000;
        border-color: #000000;
        border-width: 19px;
        padding: 10px 32px;
        margin-top: 25px;
        box-shadow: 0px 0px 0px 0px rgb(0,0,0);
    }
    
    [data-baseweb="input"] {
        border-radius: 53px;
        border-style: solid;
        border-width: 5px;
    }
    
    
</style>""", unsafe_allow_html=True)    


# m = st.markdown("""
# <style>
#     div.stButton > button:first-child {
#         color:#ffffff;
#         border-radius: 53px;
#     }
#     div.stButton > button:hover {
#         background-color: #000000;
#         color:#ff0000;
#         border-radius: 53px;
#         }
# </style>""", unsafe_allow_html=True)

# st.markdown(
#         """
#     <style>
#     .stButton>button {
#         border-radius: 53px;
#     }
#     </style>
#     """,
#         unsafe_allow_html=True,
#     )


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



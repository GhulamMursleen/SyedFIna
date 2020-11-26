#!/usr/bin/env python
# coding: utf-8

# In[1]:


############Import Libraries
import numpy as np
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import re
from sklearn.utils import shuffle
import nltk
import pandas as pd
#nltk.download('stopwords')
from fuzzywuzzy import process,fuzz
import pickle
try:
    from nltk.corpus import stopwords
except:
    pass


# In[2]:
class Model:

    def train(self):
        try:
            df = pd.read_csv("./ClauseCollection.csv",usecols=['description','tags'])
            df=df.dropna()
            dfs = dict(tuple(df.groupby('tags')))
            i=0
            for x in df["tags"].unique():
                if len(dfs[x]["description"].tolist())>80:
                    txt=dfs[x].head(80)
                    if i==0:
                        i=i+1
                        data=txt
                        #print(type(data))
                    else:
                        data=pd.concat([data, txt])
            data=shuffle(data)
            X=data["description"].tolist()
            y=data["tags"].tolist()
            documents = []



            stemmer = WordNetLemmatizer()
            
            for sen in range(0, len(X)):
                # Remove all the special characters
                document = re.sub(r'\W', ' ', str(X[sen]))
                
                # remove all single characters
                document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
                
                # Remove single characters from the start
                document = re.sub(r'\^[a-zA-Z]\s+', ' ', document) 
                
                # Substituting multiple spaces with single space
                document = re.sub(r'\s+', ' ', document, flags=re.I)
                
                # Removing prefixed 'b'
                document = re.sub(r'^b\s+', '', document)
                
                # Converting to Lowercase
                document = document.lower()
                
                # Lemmatization
                document = document.split()
            
                document = [stemmer.lemmatize(word) for word in document]
                document = ' '.join(document)
                
                documents.append(document)
                
            
            
            vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
            X = vectorizer.fit_transform(documents).toarray()
            
            
            
            
            tfidfconverter = TfidfTransformer()
            X = tfidfconverter.fit_transform(X).toarray()
            
            
            
            tfidfconverter = TfidfVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
            X = tfidfconverter.fit_transform(documents).toarray()
            
            
            
            
           # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
            
            classifier = RandomForestClassifier(n_estimators=1000, random_state=0)
            #classifier.fit(X_train, y_train) 
            classifier.fit(X, y) 
            #y_pred = classifier.predict(X_test)
            
            # save the model to disk
            filename = 'finalized_model.sav'
            pickle.dump(classifier, open(filename, 'wb'))
            return "Successfully Trained"
        except:
            return "Successfully Trained"
    #recommendation("1")  
    
    
    # In[13]:
    
    
    def predict(self,X):
        
        XX=X
        try:
            stemmer = WordNetLemmatizer()
            documents = []
            for sen in range(0, len(X)):
                # Remove all the special characters
                document = re.sub(r'\W', ' ', str(X[sen]))
                
                # remove all single characters
                document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)
                
                # Remove single characters from the start
                document = re.sub(r'\^[a-zA-Z]\s+', ' ', document) 
                
                # Substituting multiple spaces with single space
                document = re.sub(r'\s+', ' ', document, flags=re.I)
                
                # Removing prefixed 'b'
                document = re.sub(r'^b\s+', '', document)
                
                # Converting to Lowercase
                document = document.lower()
                
                # Lemmatization
                document = document.split()
            
                document = [stemmer.lemmatize(word) for word in document]
                document = ' '.join(document)
                
                documents.append(document)
                
            
            
            vectorizer = CountVectorizer(max_features=1500 ,stop_words=stopwords.words('english'))
            X = vectorizer.fit_transform(documents).toarray()
            
            
            
            
            tfidfconverter = TfidfTransformer()
            X = tfidfconverter.fit_transform(X).toarray()
            
            
            
            tfidfconverter = TfidfVectorizer(max_features=1500,stop_words=stopwords.words('english'))
            X = tfidfconverter.fit_transform(documents).toarray()
            filename = 'finalized_model.sav'
            loaded_model = pickle.load(open(filename, 'rb'))
            Filename="./ClauseCollection.csv"
            df = pd.read_csv(Filename,usecols=['description','tags'],  error_bad_lines=False)
            df = df.dropna()
            descriptions=df['description'].tolist()
            tagss=df['tags'].tolist()
            result=[]
            for x in XX:
                results=process.extract(x, descriptions, scorer=fuzz.token_sort_ratio)
                #print("results",results[0])
                result.append({"clauseText":x,"tag":tagss[descriptions.index(results[0][0])]})
            #result = loaded_model.predict(X)
            
            return result
        except Exception as e:
            filename = 'finalized_model.sav'
            loaded_model = pickle.load(open(filename, 'rb'))
            Filename="./ClauseCollection.csv"
            df = pd.read_csv(Filename,usecols=['description','tags'],  error_bad_lines=False)
            df = df.dropna()
            descriptions=df['description'].tolist()
            tagss=df['tags'].tolist()
            result=[]
            for x in XX:
                results=process.extract(x, descriptions, scorer=fuzz.token_sort_ratio)
                #print("results",results[0])
                result.append({"clauseText":x,"tag":tagss[descriptions.index(results[0][0])]})
            #result = loaded_model.predict(X)
            
            return result
    #newsfeed("News")
    
    def __init__(self):
        print("Start Model")
    
    # In[ ]:





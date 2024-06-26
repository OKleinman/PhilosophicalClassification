# -*- coding: utf-8 -*-


"""# Data Set Import, Libraries Import"""

!pip install kaggle

! mkdir ~/.kaggle

! cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

! kaggle datasets download kouroshalizadeh/history-of-philosophy

! unzip history-of-philosophy.zip


# Load, explore and plot data
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# Train test split
from sklearn.model_selection import train_test_split


# Text pre-processing
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping


# Modeling
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Embedding, Dropout, GlobalAveragePooling1D, Flatten, SpatialDropout1D, Bidirectional

import keras


"""# Visualizing the Data"""

df = pd.read_csv("philosophy_data.csv")

df.info()

df.describe()

df.groupby('school').describe().T

df.head()


"""# Class Undersampling"""

plt.figure(figsize=(16,5))
sns.countplot(df.school)
plt.title('The distribution of data across schools')

no_sample = 17957
df=df.groupby(
    "school",
    as_index=False,
    group_keys=False
  ).apply(
    lambda s: s.sample(no_sample,replace=True)
)

plt.figure(figsize=(16,5))
sns.countplot(df.school)
plt.title('The distribution of data across schools')


"""# Drop Classes"""

#drop columns
df = df.loc[df["school"] != "stoicism"]
df = df.loc[df["school"] != "plato"]
df = df.loc[df["school"] != "aristotle"]
df = df.loc[df["school"] != "phenomenology"]
df = df.loc[df["school"] != "german_idealism"]
df = df.loc[df["school"] != "Nietzsche"]


"""# Data Augmentation"""

df['text_length'] = df['sentence_str'].apply(len)

df['phil_type'] = df['school'].map({'analytic':0, 'continental':1, 'empiricism':2, 'rationalism':3, 'capitalism':4, 'communism':5, 'feminism':6,})

phil_school = df['phil_type'].values
df.head()

df.info()


"""# Basic LSTM"""

wordcountmax = 50000
seqlenmax = 250
dimension = 100
tokenizer = Tokenizer(num_words=wordcountmax, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
tokenizer.fit_on_texts(df['sentence_lowered'].values)
word_index = tokenizer.word_index

X = tokenizer.texts_to_sequences(df['sentence_lowered'].values)
X = pad_sequences(X, maxlen=seqlenmax)

Y = pd.get_dummies(df['school']).values

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.10, random_state = 42)

model = Sequential()
model.add(Embedding(wordcountmax, dimension, input_length=X.shape[1]))
model.add(SpatialDropout1D(0.2))
model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(7, activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

epochs = 1
batch = 64

history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch, validation_split=0.1)


"""# LSTM + W2V"""

from bs4 import BeautifulSoup
import re
import nltk

from nltk.corpus import stopwords
from nltk import word_tokenize,sent_tokenize
from nltk.stem import PorterStemmer,LancasterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk import ne_chunk

from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.model_selection import train_test_split,cross_validate
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV

import keras
from keras.preprocessing.text import one_hot,Tokenizer
from keras.models import Sequential
from keras.layers import Dense , Flatten ,Embedding,Input,CuDNNLSTM,LSTM
from keras.models import Model
from keras.preprocessing.text import text_to_word_sequence

from gensim.models import Word2Vec

def clean_reviews(review):
    review_text = re.sub("[^a-zA-Z]"," ",review_text)
    word_tokens = review_text.lower().split()
    le = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    word_tokens = [le.lemmatize(w) for w in word_tokens if not w in stop_words]
    cleaned_review =" ".join(word_tokens)
    return cleaned_review

sentences = []
for i in range(len(df.tokenized_txt)):
    alphatized = re.sub("[^a-zA-Z]"," ", df['sentence_str'].iloc[i])
    temp_array = alphatized.split(' ')
    temp_array = list(filter(None, temp_array))
    sentences.append(temp_array)

import gensim
w2v_model=gensim.models.Word2Vec(sentences=sentences,size=300,window=10,min_count=1)

w2v_model.train(sentences,epochs=10,total_examples=len(sentences))

w2v_model.wv.get_vector('good')

vocab=w2v_model.wv.vocab

print("The total number of words are : ", len(vocab))

w2v_model.wv.most_similar('good')

w2v_model.wv.similarity('wood','stone')

print("The no of words :",len(vocab))

vocab=list(vocab.keys())

word_vec_dict={}
for word in vocab:
  word_vec_dict[word]=w2v_model.wv.get_vector(word)
print("The no of key-value pairs : ",len(word_vec_dict))

maxi=-1
for i,rev in enumerate(df['sentence_str']):
    tokens=rev.split()
    if(len(tokens)>maxi):
        maxi=len(tokens)
print(maxi)

tok = Tokenizer()
tok.fit_on_texts(df['sentence_str'])
vocab_size = len(tok.word_index) + 1
encd_rev = tok.texts_to_sequences(df['sentence_str'])

max_rev_len = 253
vocab_size = len(tok.word_index) + 1
embed_dim = 300

pad_rev= pad_sequences(encd_rev, maxlen=max_rev_len, padding='post')
pad_rev.shape

embed_matrix=np.zeros(shape=(vocab_size,embed_dim))
for word,i in tok.word_index.items():
  embed_vector=word_vec_dict.get(word)
  if embed_vector is not None:
    embed_matrix[i]=embed_vector

print(embed_matrix[14])

Y=keras.utils.to_categorical(df['phil_type'])
x_train,x_test,y_train,y_test=train_test_split(pad_rev,Y,test_size=0.20,random_state=42)

from keras.initializers import Constant
from keras.layers import ReLU
from keras.layers import Dropout
model=Sequential()
model.add(Embedding(input_dim=vocab_size,output_dim=embed_dim,input_length=max_rev_len,embeddings_initializer=Constant(embed_matrix)))
model.add(CuDNNLSTM(64,return_sequences=False))
model.add(Flatten())
model.add(Dense(7,activation='relu'))
model.add(Dropout(0.50))
model.add(Dense(7,activation='softmax'))

model.summary()


"""# BiLSTM + W2V"""

bi_model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embed_dim),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(embed_dim)),
    tf.keras.layers.Dense(embed_dim, activation='relu'),
    tf.keras.layers.Dense(7, activation='softmax')
])
bi_model.summary()

bi_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
epochs = 10
history = bi_model.fit(x_train, y_train, epochs=epochs, validation_data=(x_test,y_test))


"""# *save and load model*"""

bi_model.save('/content/drive/MyDrive/KaggleData')

bi_model = keras.models.load_model('/content/drive/MyDrive/KaggleData')


"""# Evaluation"""

accr = bi_model.evaluate(x_test,y_test)
print('Test set\n  Loss: {:0.3f}\n  Accuracy: {:0.3f}'.format(accr[0],accr[1]))

plt.title('Accuracy')
plt.plot(history.history['accuracy'], label='train')
plt.plot(history.history['val_accuracy'], label='test')
plt.legend()
plt.show()

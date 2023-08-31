import re
import spacy
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from spacy.lang.en import stop_words
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

# Load English pipeline
nlp = spacy.load('en_core_web_md')

# Load the dataset from CSV and remove rows with missing values
# Source: https://www.kaggle.com/datasets/kazanova/sentiment140
# This is the sentiment140 dataset. It contains 1,600,000 tweets extracted using the Twitter API.
data = pd.read_csv('Twitter_Data_024.csv', names=["target", "ids", "date", "flag", "user", "TweetText"], encoding='latin-1')
data.drop(['ids','date','flag','user'], axis = 1, inplace = True)
data.columns = ['label', 'tweet']
data.dropna(subset = ['tweet', 'label'], inplace=True)

# Define a mapping of sentiment labels (0 = negative, 2 = neutral, 4 = positive)
sentiment_mapping = {
    4: 'positive',
    2: 'neutral',
    0: 'negative'
}

# Preprocess the text
stop_words = stop_words.STOP_WORDS
def preprocess_text(text):
    # Handling NaN values
    if isinstance(text, float) and np.isnan(text):
        return ""
    
    # Converting text to lowercase
    text = text.lower()
    
    # Removing special characters, URLs, and mentions
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Tokenize and remove stop words
    tokens = nlp(text)
    tokens_without_stop = [token.lemma_ for token in tokens if token.text not in stop_words]
    return " ".join(tokens_without_stop)

# Prepare the dataset
data['tweet'] = data['tweet'].apply(preprocess_text)
tweets = data['tweet']
labels = data['label']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(tweets, labels, test_size=0.2, random_state=42)

# Vectorize text data using CountVectorizer
vectorizer = CountVectorizer(stop_words='english')
X_train_vectors = vectorizer.fit_transform(X_train)
X_test_vectors = vectorizer.transform(X_test)

# Train and evaluate the Support Vector Machine (SVM) classifier
svm_classifier = SVC(kernel='linear', gamma='scale', C=1.0)
svm_classifier.fit(X_train_vectors, y_train)

y_pred_svm = svm_classifier.predict(X_test_vectors)
accuracy_svm = accuracy_score(y_test, y_pred_svm)
print("SVM Accuracy:", accuracy_svm)

# Train and evaluate the RandomForestClassifier
rf_classifier = RandomForestClassifier(n_estimators=1000, random_state=42)
rf_classifier.fit(X_train_vectors, y_train)

y_pred_rf = rf_classifier.predict(X_test_vectors)
accuracy_rf = accuracy_score(y_test, y_pred_rf)
print("Random Forest Accuracy:", accuracy_rf)

# Test both classifiers on example tweets
example_tweets = [
    "I had an amazing day at the beach!",
    "Just finished a great book. Highly recommended.",
    "The weather is so-so today.",
    "I'm feeling indifferent about the new movie.",
    "The service at the restaurant was terrible.",
    "I can't believe how rude the customer support was.",
    "This product exceeded my expectations.",
    "The traffic is a nightmare this morning.",
    "Feeling a bit down today.",
    "The concert was a disappointment."
]

for tweet in example_tweets:
    example_tweet_vector = vectorizer.transform([preprocess_text(tweet)])
    predicted_sentiment_svm = svm_classifier.predict(example_tweet_vector)
    predicted_sentiment_rf = rf_classifier.predict(example_tweet_vector)
    predicted_sentiment_label_svm = sentiment_mapping[predicted_sentiment_svm[0]]
    predicted_sentiment_label_rf = sentiment_mapping[predicted_sentiment_rf[0]]
    print(f"Tweet: {tweet}")
    print(f"SVM Predicted sentiment: {predicted_sentiment_label_svm}")
    print(f"Random Forest Predicted sentiment: {predicted_sentiment_label_rf}\n")


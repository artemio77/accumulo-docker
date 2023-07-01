import json

import nltk
import pandas as pd
import spacy
import torch
from nltk import PunktSentenceTokenizer, word_tokenize, pos_tag
from nltk.corpus import stopwords
from sympy.physics.quantum.identitysearch import scipy
from transformers import BertTokenizer, AutoTokenizer, AutoModelForSequenceClassification


def load_spacy_model():
    return spacy.load("en_core_web_sm")


def get_sentences(text):
    sentence_tokenizer = PunktSentenceTokenizer()
    sentences = sentence_tokenizer.tokenize(text, )
    sentences = [text for text in sentences if len(text.split()) > 6]
    max_length = 500
    transformed_sentences = []
    sentence_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    for sentence in sentences:
        # Tokenize sentence
        tokens = sentence_tokenizer.tokenize(sentence)
        if len(tokens) > max_length:
            # Truncate the tokens to the maximum length
            tokens = tokens[:max_length]
        transformed_sentence = sentence_tokenizer.convert_tokens_to_string(tokens)
        transformed_sentences.append(transformed_sentence)
    return transformed_sentences


def perform_sentiment_analysis(sentences):
    # finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
    # tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
    # nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer)
    # results = nlp(sentences)
    # sentiment = pd.DataFrame({
    #     "docs": sentences,
    #     "label": [r["label"] for r in results],
    #     "score": [r["score"] for r in results]
    # })

    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    scores_list = []
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt")
        with torch.no_grad():
            logits = model(**inputs).logits
        scores = {k: v for k, v in zip(model.config.id2label.values(), scipy.special.softmax(logits.numpy().squeeze()))}
        sentiment = max(scores, key=scores.get)
        max_score = max(scores.values())
        data = {
            "Sentence": sentence,
            "Positive": scores["positive"],
            "Negative": scores["negative"],
            "Neutral": scores["neutral"],
            "Sentiment": sentiment,
            "MaxScore": max_score,
        }
        scores_list.append(data)

    sentiment = pd.DataFrame(scores_list)

    return sentiment


def extract_nouns(sentiment):
    # Tokenize the text into sentences
    pos_lst = []
    for sentence in list(sentiment["Sentence"]):
        # Tokenize the sentence into words
        words = word_tokenize(sentence)

        # Filter out stopwords and punctuations
        filtered_words = [word.lower() for word in words if
                          word.isalpha() and word.lower() not in stopwords.words('english')]

        # Perform part-of-speech tagging
        tagged_words = pos_tag(filtered_words)
        # Initialize an empty list to store the nouns
        # Extract nouns (NN, NNS, NNP, NNPS tags)
        nouns = []
        nouns.extend([word for word, pos in tagged_words if pos.startswith('NN')])
        pos_lst.append(nouns)
    sentiment["pos_nn"] = pos_lst
    return sentiment


def get_report(ticker, report_type):
    file_path = f"data/result/{ticker}/{ticker}-{report_type}.json"
    with open(file_path, 'r') as file:
        report = json.load(file)
    return report


def analyze_report(ticker, report_type):
    report = get_report(ticker, report_type)

    sentences_annual_report = get_sentences(report.get("text"))
    print(f"Total sentences: {len(sentences_annual_report)}")

    sentiment = perform_sentiment_analysis(sentences_annual_report)

    summary_for_limit(ticker, sentiment, 50)
    mean_sentiment(sentiment)


def mean_sentiment(sentiment):
    pos_lst = []
    for sentence in sentiment.Sentence:
        # Tokenize the sentence into words
        words = word_tokenize(sentence)

        # Filter out stopwords and punctuations
        filtered_words = [word.lower() for word in words if
                          word.isalpha() and word.lower() not in stopwords.words('english')]

        # Perform part-of-speech tagging
        tagged_words = pos_tag(filtered_words)
        # Initialize an empty list to store the nouns
        # Extract nouns (NN, NNS, NNP, NNPS tags)
        nouns = []
        nouns.extend([word for word, pos in tagged_words if pos.startswith('NN')])
        pos_lst.append(nouns)
    sentiment["pos_nn"] = pos_lst
    sentiment['label_int'] = sentiment['Sentiment'].map({"Neutral": 0, "Negative": -1, "Positive": 1})
    sentiment['score_new'] = sentiment.apply(lambda x: x['MaxScore'] * x['label_int'], axis=1)

    sentiment_nn = sentiment.query("Sentiment != 'Neutral'")[["pos_nn", "score_new"]].explode("pos_nn")
    sentiment_nn = sentiment_nn.groupby("pos_nn") \
        .agg({"score_new": ['count', 'mean']}) \
        .reset_index().set_axis(["pos_nn", "cnt", "mean_sentiment"], axis="columns")
    sentiment_nn.columns = ["pos_nn", "cnt", "mean_sentiment"]

    result = pd.concat([sentiment_nn.query("cnt > 5").query("mean_sentiment > 0.1")
                       .sort_values("mean_sentiment", ascending=False).head(20),
                        sentiment_nn.query("cnt > 10").query("mean_sentiment < -0.5")
                       .sort_values("mean_sentiment").head(20)]).reset_index(drop=True)

    print(f"{result}")
    mean_sentiment_results = result.to_dict()
    with open('mean_sentiment_results.json', 'w') as f:
        json.dump(mean_sentiment_results, f, indent=4)


def summary_for_limit(ticker, sentiment, limit):
    positive_sentiment = sentiment[sentiment.get("Sentiment") == "positive"] \
        .sort_values("Positive", ascending=False).head(limit).to_dict("records")
    negative_sentiment = sentiment[sentiment.get("Sentiment") == "negative"] \
        .sort_values("Negative", ascending=False).head(limit).to_dict("records")
    neural_sentiment = sentiment[sentiment.get("Sentiment") == "neutral"] \
        .sort_values("Neutral", ascending=False).head(limit).to_dict("records")
    count_table = sentiment.groupby(["Sentiment"]).size().reset_index(name='counts')
    print(f"Top {limit} statistic: {count_table}")

    with open(f"data/result/{ticker}/positive_sentiment_results.json", 'w') as f:
        json.dump(positive_sentiment, f, indent=4)
    with open(f"data/result/{ticker}/negative_sentiment_results.json", 'w') as f:
        json.dump(negative_sentiment, f, indent=4)

    total_positive = sum(summary["Positive"] for summary in positive_sentiment + negative_sentiment + neural_sentiment)
    total_negative = sum(summary["Negative"] for summary in positive_sentiment + negative_sentiment + neural_sentiment)
    total_neutral = sum(summary["Neutral"] for summary in positive_sentiment + negative_sentiment + neural_sentiment)

    weights = {
        "Positive": 1.1,
        "Negative": 0.9,
        "Neutral": 0.3
    }

    # Adjust sentiment scores proportionally to sum up to 100
    total_sum = (weights["Positive"] * total_positive) + (weights["Negative"] * total_negative) + (
            weights["Neutral"] * total_neutral)
    aggregated_summary = {
        "Positive": (100 / total_sum) * (weights["Positive"] * total_positive),
        "Negative": (100 / total_sum) * (weights["Negative"] * total_negative),
        "Neutral": (100 / total_sum) * (weights["Neutral"] * total_neutral),
    }

    # Determine the aggregated sentiment based on the adjusted scores
    if aggregated_summary["Positive"] > aggregated_summary["Negative"]:
        if aggregated_summary["Positive"] > aggregated_summary["Neutral"]:
            aggregated_summary["Sentiment"] = "Positive"
        else:
            aggregated_summary["Sentiment"] = "Neutral"
    elif aggregated_summary["Negative"] > aggregated_summary["Neutral"]:
        aggregated_summary["Sentiment"] = "Negative"
    else:
        aggregated_summary["Sentiment"] = "Neutral"

    print("Aggregated Summary:")
    for key, value in aggregated_summary.items():
        print(f"{key}: {value}")


if __name__ == '__main__':
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    analyze_report("SNOW", "8-K")

# Total sentences: 10
# Total sentences: 20
# Total sentences: 50
# Total sentences: 100

from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS
from konlpy.tag import Okt
from nltk import word_tokenize, pos_tag
from fuzzywuzzy import fuzz
from googletrans import Translator
import nltk
import re
import json
import os
from db_connect import get_db

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
CORS(app)

# To run this app in a local environment, you need to add the following setting ['JAVA_HOME'].
# os.environ['JAVA_HOME'] = 'C:/Program Files/Java/jdk-17.0.4'
okt = Okt()
translator = Translator()


@app.route('/')
def home():
    return 'hello meca data server'


@app.route('/api/keywords', methods=['POST'])
def post_nouns():
    try:
        data = request.get_json()
        sentence = data['sentence']
        user_id = data['userId']
        eng_list = extract_english_keyword(sentence)
        kor_list = extract_korean_keyword(sentence)
        combined_list = eng_list + kor_list
        filtered_list = [word for word in combined_list if len(word) > 1]
        keyword_counts = Counter(filtered_list)
        result = {}
        for key, value in keyword_counts.items():
            result[key] = value
        get_db().keywords.update_many({'user_id': user_id}, {'$inc': result}, upsert=True)
        return jsonify({'keyword': result})
    except:
        return jsonify({'message': 'bad request'}), 400


@app.route('/api/keywords/<string:user_id>', methods=['GET'])
def get_nouns(user_id):
    try:
        data = get_db().keywords.find_one({'user_id': user_id}, {'_id': False})
        return jsonify({'keywords': data, 'user': user_id})
    except:
        return jsonify({'message': 'bad request'}), 400


@app.route('/api/scores/<string:user_id>', methods=['GET'])
def get_scores(user_id):
    try:
        data = get_db().scores.find_one({'user_id': user_id}, {'_id': False})
        return jsonify({'totalScore': data['total_score'], 'count' : data['count'], 'user': user_id})
    except:
        return jsonify({'message': 'bad request'}), 400


@app.route('/api/scores', methods=['POST'])
def post_scores():
    try:
        data = request.get_json()
        answer = (data['answer']).upper()
        input_value = (data['input']).upper()
        user_id = data['userId']
        score = max(get_string_distance(input_value, answer),
                    get_string_distance(get_translated_text(input_value), get_translated_text(answer)))
        weighted_score = get_weighted_score(score)
        get_db().scores.update_one({'user_id': user_id}, {'$inc': {'count': 1, 'total_score': weighted_score}},
                                   upsert=True)
        return jsonify({'score': weighted_score})
    except:
        return jsonify({'message': 'bad request'}), 400


def extract_english_keyword(keyword):
    english_text = re.sub('[^a-zA-Z]', ' ', keyword)
    english_tagged = pos_tag(word_tokenize(english_text))
    english_noun_list = [word for word, pos in english_tagged if pos in ['NN', 'NNS', 'NNP', 'NNPS']]
    return english_noun_list


def extract_korean_keyword(keyword):
    korean_text = re.sub('[^가-힣]', ' ', keyword)
    return okt.nouns(okt.normalize(korean_text))


def get_string_distance(input_string, answer):
    if len(input_string) == 1 and len(answer) == 1:
        return fuzz.ratio(input_string, answer)
    return fuzz.token_sort_ratio(input_string, answer)


def get_translated_text(text):
    result = translator.translate(text, dest='en')
    return result.text.upper()


def get_weighted_score(score):
    if score == 100:
        return score
    return round(score ** 0.965)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS
from konlpy.tag import Okt
from nltk import word_tokenize, pos_tag
from googletrans import Translator
import nltk
import re
import json
import os
from db_connect import get_db

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

stopwords = nltk.corpus.stopwords.words('english')
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
        eng_dict = extract_english_keyword(sentence)
        eng_list = [d['morph'] for d in eng_dict]
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


@app.route('/api/morpheme', methods=['PUT'])
def put_morpheme():
    try:
        data = request.get_json()
        user_answer = data['userAnswer']
        card_answer = data['cardAnswer']
        user_answer_morpheme = extract_english_keyword(get_translated_text(user_answer))
        card_answer_morpheme = extract_english_keyword(get_translated_text(card_answer))
        return jsonify({"userAnswerMorpheme": user_answer_morpheme, "cardAnswerMorpheme": card_answer_morpheme})
    except:
        return jsonify({'message': 'bad request'}), 400


def extract_english_keyword(keyword):
    english_text = re.sub('[^a-zA-Z]', ' ', keyword)
    english_tagged = pos_tag(word_tokenize(english_text))
    english_list = []
    for word, pos in english_tagged:
        if word.lower() not in stopwords:
            extracted = {'morph': word, 'pos': pos}
            english_list.append(extracted)
    return english_list


def extract_korean_keyword(keyword):
    korean_text = re.sub('[^가-힣]', ' ', keyword)
    return okt.nouns(okt.normalize(korean_text))


def get_translated_text(text):
    result = translator.translate(text, dest='en')
    return result.text.upper()


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS
from konlpy.tag import Okt
from nltk import word_tokenize, pos_tag
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


@app.route('/')
def home():
    return 'hello meca data server'


@app.route('/api/nouns', methods=['POST'])
def post_nouns():
    try:
        data = request.get_json()
        sentence = data['sentence']
        user_id = data['userId']
        eng_list = extract_english_keyword(sentence)
        kor_list = extract_korean_keyword(sentence)
        keyword_counts = Counter(eng_list + kor_list)
        result = {}
        for key, value in keyword_counts.items():
            result[key] = value
        get_db().hello.update_many({'user_id': user_id}, {'$inc': result}, upsert=True)
        return json.dumps(result, ensure_ascii=False)
    except:
        return jsonify({'message': 'bad request'}), 400


@app.route('/api/nouns/<string:user_id>', methods=['GET'])
def get_nouns(user_id):
    try:
        data = get_db().hello.find_one({'user_id': user_id}, {'_id': False})
        return json.dumps({'keywords': data, 'user': user_id}, ensure_ascii=False)
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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

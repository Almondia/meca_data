## meca_data

> 데이터 분석용 api server

<br>

### Stack

- python 3.8
- flask 2.3.2
- mongodb
- nltk, konlpy
- docker, github-actions

<br>

### Api

| METHOD | URI             | Request                                | Response                                                | Description  |
|------|-----------------|----------------------------------------|---------------------------------------------------------|--------------|
| POST | /api/nouns      | {'userId': string, 'sentence': string } | {'keywords': {[key: string]: number }}                  | 문장으로 키워드 등록  |
| GET  | /api/nouns/{userId} |      | {'keywords': {[key: string]: number }, 'user': string } | 유저 키워드 목록 조회 |
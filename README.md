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

| METHOD | URI                    | Request                                                | Response          | Description      |
|--------|------------------------|--------------------------------------------------------|-------------------|------------------|
| POST   | /api/keywords          | {'userId': string, 'sentence': string }                | {'keywords': {[key: string]: number }} | 문장으로 키워드 등록      |
| GET    | /api/keywords/{userId} |                                                        | {'keywords': {[key: string]: number }, 'user': string } | 유저 키워드 목록 조회     |
| POST   | /api/scores            | {'answer': string, 'input': string, 'userId': string } | {'score': number} | 사용자 입력 답 스코어 등록  |
| GET    | /api/scores/{userId}   |                                                        | {'answer': string, 'input': string, 'userId': string }  | 사용자 획득 총합 스코어 조회 |

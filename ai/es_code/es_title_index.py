from elasticsearch import Elasticsearch

# 제목 검색 인덱스 세팅

index_settings = {
    "settings": {
        "analysis": {
            "analyzer": {
                "korean_analyzer": {
                    "type": "custom",
                    "tokenizer": "korean_tokenizer",
                    "filter": [
                        "lowercase",
                        "nori_filter",
                        "edge_ngram_filter_front",
                        "edge_ngram_filter_back",
                        "trim",
                    ],
                },
            },
            "tokenizer": {
                "korean_tokenizer": {
                    "type": "nori_tokenizer",
                    "decompound_mode": "mixed",
                },
            },
            "filter": {
                "word_filter": {
                    "type": "stop",
                    "stopwords": ["주"],
                },
                "nori_filter": {
                    "type": "nori_part_of_speech",
                    "stoptags": [
                        "E",
                        "IC",
                        "J",
                        "MAG",
                        "MAJ",
                        "MM",
                        "SP",
                        "SSC",
                        "SSO",
                        "SC",
                        "SE",
                        "XPN",
                        "XSA",
                        "XSN",
                        "XSV",
                        "UNA",
                        "NA",
                        "VSV",
                        "VV",
                    ],
                },
                "edge_ngram_filter_front": {
                    "type": "edge_ngram",
                    "min_gram": "1",
                    "max_gram": "10",
                    "side": "front",
                },
                "edge_ngram_filter_back": {
                    "type": "edge_ngram",
                    "min_gram": "1",
                    "max_gram": "10",
                    "side": "back",
                },
            },
        },
    },
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "korean_analyzer",
            }
        }
    },
}


es = Elasticsearch(hosts="http://localhost:9200")

r = es.indices.create(index="demo1-title-data", body=index_settings)

print(r)

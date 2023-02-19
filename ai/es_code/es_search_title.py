from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="http://localhost:9200")

# 제목검색


def search_title_es(query):
    body = {
        "query": {
            "bool": {
                "should": [
                    {"term": {"title": query}},
                ]
            }
        }
    }
    resp = es.search(index="demo1-title-data", body=body)
    result = []
    for i in resp["hits"]["hits"]:
        result.append(i["_source"]["title"])
    return result


if __name__ == "__main__":
    print(search_title_es("삼성"))

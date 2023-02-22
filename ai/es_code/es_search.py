from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="http://localhost:9200")
index = "demo1-test-data"


def search_es(query):

    """
    질문으로 보고서 context 검색
    """
    query = query.replace("누구","").replace("어디","").replace("무엇","").replace("얼마","").replace("언제","")
    body = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"title": {"query": query, "boost": 3}}},
                    {"match": {"context": {"query": query, "boost": 1}}},
                ],
                "minimum_should_match": 0,
            }
        },
        "from": 0,
        "size": 20,
    }
    resp = es.search(index=index, body=body)
    result = []
    for i in resp["hits"]["hits"]:
        result.append({"title": i["_source"]["title"], "context": i["_source"]["context"]})
    return result


def search_es2(query, title):
    """
    보고서 이름이 주어진 상태에서 검색어로 유사도 검색
    """
    body = {
        "query": {
            "bool": {
                "must": [{"match": {"title": {"query": title, "operator": "and"}}}],
                "should": [{"match": {"context": {"query": query, "boost": 1}}}],
            }
        },
        "from": 0,
        "size": 5,
    }
    resp = es.search(index=index, body=body)
    result = []
    for i in resp["hits"]["hits"]:
        result.append({"title": i["_source"]["title"], "context": i["_source"]["context"]})
    return result


def search_context_with_title(query):
    """
    보고서 이름 검색
    """
    body = {
        "query": {
            "match": {
                "title": {
                    "query": query,
                    "operator": "and",
                },
            },
        },
    }

    resp = es.search(index=index, body=body)
    result = []
    for i in resp["hits"]["hits"]:
        result.append({"title": i["_source"]["title"], "context": i["_source"]["context"]})
    return result


if __name__ == "__main__":
    tmp = search_context_with_title("삼성전자주식회사 사업보고서 20210101 20211231")
    for i in tmp:
        print(i["title"])

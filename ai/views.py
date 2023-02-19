from django.shortcuts import render
from .es_code.es_search import search_es, search_context_with_title, search_es2
from .es_code.es_search_title import search_title_es
from .apps import AiConfig
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def home(request):
    result = {}
    if request.method == "POST":
        json_body = json.loads(request.body.decode("utf-8"))
        query = json_body["query"]
        if "title" in json_body and json_body["title"] != None:
            # 질문과 보고서 이름이 들어온 경우
            context_title = json_body["title"]
            input_set = search_es2(query, context_title)
            if len(input_set) == 0:
                return JsonResponse(
                    {
                        "query": query,
                        "answer": None,
                    }
                )
            print("searched!")
            title = input_set[0]["title"]
            context = input_set[0]["context"]

        else:
            # 질문만 들어온 경우
            context_title = None
            print("query : ", query)
            input_set = search_es(query)
            if len(input_set) == 0:
                return JsonResponse(
                    {
                        "query": query,
                        "answer": None,
                    }
                )

            title = input_set[0]["title"]
            context = input_set[0]["context"]

        answer = AiConfig.qa_model.predict_long_string(query, context)
        answer = sorted(answer, key=lambda d: d["probability"], reverse=True)
        result = {
            "query": query,
            "answer": answer,
            "title": title,
            "context": context[:300],
        }
        return JsonResponse(result)


@csrf_exempt
def search(request):
    """
    보고서 이름 검색
    """
    if request.method == "GET":
        keyword = request.GET.get("keyword")
        search_result = search_title_es(keyword)
        return JsonResponse({"result": search_result})

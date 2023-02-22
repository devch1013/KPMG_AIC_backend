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
        # if "XI" in input_set[0]["context"]:
        #     input_set.pop(0)
        context = clean_context(input_set[0]["context"])
        # if len(context) // 250 > 600:
        #     return JsonResponse(
        #             {
        #                 "query": query,
        #                 "answer": None,
        #             }
        #         )
        for i in input_set[1:]:
            print("context length: ", (len(context) + len(i["context"]))//250)
            tmp_context = clean_context(i["context"])
            if (len(context) + len(tmp_context))//250 < 600:
                context += tmp_context
            else:
                break
        answer = AiConfig.qa_model.predict_long_string(query, context)
        answer = sorted(answer, key=lambda d: d["probability"], reverse=True)
        for i in answer:
            if i["probability"] < 1.99:
                break
            if "<table>" in i["answer"]:
                answer.insert(0, i)
                break
        result = {
            "query": query,
            "answer": answer[:5],
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
    
    
def clean_context(context):
    return context.replace("\n", " ").replace("<div>", "").replace("</div>", "")

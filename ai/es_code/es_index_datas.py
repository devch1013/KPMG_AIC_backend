from elasticsearch import Elasticsearch
from datetime import datetime
import re, html
import os

# 보고서 데이터 색인
es = Elasticsearch(hosts="http://localhost:9200")
file_root = "/home/kic/Desktop/data_preprocessing_yh/preprocessed_datas"
dir_list = os.listdir(file_root)

print(len(dir_list))


def format_title(title: str) -> str:
    title = title.split("_")
    title = " ".join(title[:-1])
    return title


for idx, file in enumerate(dir_list):
    title = format_title(file)
    print(f"{idx}/{len(dir_list)}", title)
    with open(file_root + "/" + file, "r") as f:
        try:
            data = f.read()
            doc = {
                "title": title,
                "context": data,
            }

            es.index(index="demo1-data", document=doc)

        except Exception as e:
            print(e)
            continue

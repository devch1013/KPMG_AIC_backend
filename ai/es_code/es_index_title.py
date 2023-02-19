from elasticsearch import Elasticsearch
from datetime import datetime
import re, html
import os

# 제목 데이터 색인
es = Elasticsearch(hosts="http://localhost:9200")
file_root = "/home/kic/Desktop/data_preprocessing_yh/preprocessed_datas"
dir_list = os.listdir(file_root)

print(len(dir_list))


def format_title(title: str) -> str:
    title = title.split("_")
    title = " ".join(title[:-1])
    return title


exist_list = []

for idx, file in enumerate(dir_list):
    title = format_title(file)

    if title not in exist_list:
        print(f"{idx}/{len(dir_list)}", title)
        try:
            # data = f.read()
            doc = {
                "title": title,
            }

            es.index(index="demo1-title-data", document=doc)

        except Exception as e:
            print(e)
            continue
        exist_list.append(title)

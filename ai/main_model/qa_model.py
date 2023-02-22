import torch
import transformers
from datetime import datetime
import re
import torch.nn.functional as F


class QAModel:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_class = transformers.ElectraForQuestionAnswering
        model_name = "/home/kic/kpmg/demo1/ai/main_model/ckpt/checkpoint-80000"

        # Load the model
        self.model = model_class.from_pretrained(model_name).to(self.device)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(
            "monologg/koelectra-base-v3-discriminator"
        )

    def predict(self, question, context):
        context = context.replace("  "," ")
        # Encode the input text
        encoded_input = self.tokenizer(
            question, context, return_tensors="pt", padding=True, truncation=True
        ).to(self.device)

        # Generate the answer
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(**encoded_input)
            # print(outputs)
            answer_start, answer_end = (
                torch.argmax(outputs[0], dim=1).detach().cpu().numpy()[0],
                torch.argmax(outputs[1], dim=1).detach().cpu().numpy()[0],
            )
            # print(f"answer_start: {outputs[0][0][answer_start]}")
            answer = self.tokenizer.decode(
                encoded_input["input_ids"][0][answer_start : answer_end + 1],
                skip_special_tokens=True,
            )
        # decoding 띄어쓰기 제거
        answer = answer.lstrip(question).replace(" / ", "/").replace("< ", "<").replace(" >", ">")
        if answer == "" or answer == "0" or "##ows" in answer:
            return None, None
        # print("context: ",context)
        # print("answer: ",answer)
        # print(context.find(answer))
        # print(F.softmax(outputs[0], dim=1))
        return {
            "answer": answer,
            "probability": float(F.softmax(outputs[0], dim=1)[0][answer_start]) + float(F.softmax(outputs[1], dim=1)[0][answer_end]),
            "answer_start": int(answer_start),
        }, answer_start

    def predict_long_string(self, question, long_context):
        time = datetime.now()
        result_list = []
        length_limit = 500
        tmp_idx = 0
        table_start_tags, table_end_tags = find_table_tags(long_context)
        if len(long_context) > length_limit:
            for i in range(len(long_context) // length_limit):
                # 500크기의 slidinf window로 inference
                print(f"{i}/{len(long_context)//length_limit}")

                tmp_end = tmp_idx + length_limit
                if tmp_end > len(long_context):
                    tmp_end = len(long_context)
                answer, answer_start_index = self.predict(question, long_context[tmp_idx:tmp_end])

                if answer is not None:
                    # print("answer start index  ", answer_start_index)
                    # print(long_context[tmp_idx:tmp_end][answer_start_index-5:answer_start_index+1])
                    if "<td" in answer["answer"]:
                        # 테이블이 잘려나온 경우 전체 테이블 출력
                        print("table")
                        table_start, table_end = find_table_index(
                            tmp_idx + answer_start_index, table_start_tags, table_end_tags
                        )
                        # print(table_start, table_end)
                        if table_start != -1 and table_end != -1:
                            answer["answer"] = long_context[table_start:table_end]
                    result_list.append(answer)

                tmp_idx = (length_limit // 2) * (i + 1)

        else:
            return [self.predict(question, long_context)]

        print(
            f"Inference time: {datetime.now() - time}, iteration: {len(long_context)//length_limit}"
        )

        return result_list


def find_table_tags(text):
    table_start_tags = [i.start() for i in re.finditer("<table>", text)]
    table_end_tags = [i.start() + 8 for i in re.finditer("</table>", text)]

    return table_start_tags, table_end_tags


def find_table_index(idx, table_start_tags, table_end_tags):
    table_start = -1
    table_end = -1
    for s_idx in table_start_tags:
        if idx > s_idx:
            table_start = s_idx
        else:
            break
    for e_idx in table_end_tags:
        if idx < e_idx:
            table_end = e_idx
            break

    return table_start, table_end


if __name__ == "__main__":
    qa_model = QAModel()
    print(
        qa_model.predict(
            "What is Python?",
            "Python is a high-level, interpreted programming language that is used for a wide range of purposes, including web development, scientific computing, data analysis, artificial intelligence, and more.",
        )
    )

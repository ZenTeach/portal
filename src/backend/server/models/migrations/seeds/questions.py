import os
import csv
from server.models import Questions, QuestionTypeEnum, QuestionChoice
from uuid import uuid4
from random import choice

filename = "Questions.csv"
filepath = os.path.join(os.path.dirname(__file__), filename)


def question_seeds():
    with open(filepath, newline='') as fp:
        reader = csv.DictReader(fp, delimiter=',', quotechar='|')
        for line in reader:
            choices=[]
            choices.append(QuestionChoice(line["a"], 0, uuid4()))
            choices.append(QuestionChoice(line["b"], 0, uuid4()))
            choices.append(QuestionChoice(line["c"], 1, uuid4()))
            choices.append(QuestionChoice(line["d"], 0, uuid4()))
            Questions(
                question=line["Question"],
                question_type=QuestionTypeEnum.multiple_choice,
                subject="Chemistry",
                topic=line["Topic"],
                tag=line["TAG"],
                knowledge_item=line["KnowledgeItem"],
                uuid=uuid4(),
                choices=choices,
                correct_choice=choice([ x.uuid for x in choices])
            ).save()

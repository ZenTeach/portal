import os
import csv
from server.models import Questions, QuestionTypeEnum
from uuid import uuid4
from random import choices

filename = "Questions.csv"
filepath = os.path.join(os.path.dirname(__file__), filename)


def question_seeds():
    with open(filepath, newline='') as fp:
        reader = csv.DictReader(fp, delimiter=',', quotechar='|')
        for line in reader:
            choices = {'a': line["a"],
                       'b': line["b"],
                       'c': line["c"],
                       'd': line["d"]
                       }
            Questions(
                question=line["Question"],
                question_type=QuestionTypeEnum.multiple_choice,
                subject="Chemistry",
                topic=line["Topic"],
                tag=line["TAG"],
                knowledge_item=line["KnowledgeItem"],
                uuid=uuid4(),
                choices=choices
            ).save()

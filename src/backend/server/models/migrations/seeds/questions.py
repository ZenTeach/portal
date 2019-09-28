import csv
from server.models import Questions, QuestionTypeEnum
import os

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
                choices=choices,
                question_weights=0
            ).save()

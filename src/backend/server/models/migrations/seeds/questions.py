import os
import csv
from server.models import Questions, QuestionTypeEnum, QuestionChoice, ChoiceFeedback
from uuid import uuid4
from random import choice

filename = "Questions.csv"
filepath = os.path.join(os.path.dirname(__file__), filename)


def question_seeds():
    with open(filepath, newline='') as fp:
        reader = csv.DictReader(fp, delimiter=',', quotechar='|')
        for line in reader:
            choices=[]
            choice_a = QuestionChoice(line["a"], "Look at these images.", 0, uuid4())
            choice_a.save()
            choices.append(choice_a)
            choice_b = QuestionChoice(line["b"], "Revise theses lesson slides.", 0, uuid4())
            choice_b.save()
            choices.append(choice_b)
            choice_c = QuestionChoice(line["c"], "Look at these images.", 1, uuid4())
            choice_c.save()
            choices.append(choice_c)
            choice_d = QuestionChoice(line["d"], "Revise theses lesson slides.", 0, uuid4())
            choice_d.save()
            choices.append(choice_d)

            Questions(
                question=line["Question"],
                question_type=QuestionTypeEnum.multiple_choice,
                subject="Chemistry",
                topic=line["Topic"],
                tag=line["TAG"],
                knowledge_item=line["KnowledgeItem"],
                correct_choice_id=choice([ x.id for x in choices]),
                uuid=uuid4(),
                choices=choices
            ).save()

import csv
import os
from random import choice

from server.models import (KnowledgeItem, QuestionChoice, Questions,
                           QuestionTypeEnum, Subject, Topic)

filename = "Questions.csv"
filepath = os.path.join(os.path.dirname(__file__), filename)


def question_seeds():
    with open(filepath, newline="") as fp:
        reader = csv.DictReader(fp, delimiter=",", quotechar="|")
        subject_id = Subject.query.filter(Subject.name == 'Chemistry').first().id

        for line in reader:
            topic = Topic.query.filter_by(value=line["Topic"], subject_id=subject_id).first()
            if topic is None:
                topic = Topic(value=line["Topic"], subject_id=subject_id)
                topic.save()

            knowledge_item = KnowledgeItem.query.filter_by(
                value=line["KnowledgeItem"], subject_id=subject_id, topic_id=topic.id).first()
            if knowledge_item is None:
                knowledge_item = KnowledgeItem(
                    value=line["KnowledgeItem"], subject_id=subject_id, topic_id=topic.id)
                knowledge_item.save()

            q = Questions(
                question=line["Question"],
                question_type=QuestionTypeEnum.multiple_choice,
                subject_id=subject_id,
                topic=topic,
                tag=line["TAG"],
                exam_board="aqa",
                knowledge_item=knowledge_item,
                correct_choice_id=1,  # nosec
            )
            q.save()

            choices = []
            choice_a = QuestionChoice(
                line["a"], "Look at these images.", 0, None, q.id)
            choice_a.save()
            choices.append(choice_a)
            choice_b = QuestionChoice(
                line["b"], "Revise theses lesson slides.", 0, None, q.id
            )
            choice_b.save()
            choices.append(choice_b)
            choice_c = QuestionChoice(
                line["c"], "Look at these images.", 1, None, q.id)
            choice_c.save()
            choices.append(choice_c)
            choice_d = QuestionChoice(
                line["d"], "Revise theses lesson slides.", 0, None, q.id
            )
            choice_d.save()
            choices.append(choice_d)

            q.correct_choice_id = choice([x.id for x in choices])
            q.save()

import re

from server.tests.factories import ClassQuizFactory, SchoolClassFactory


def test_classquiz_set_url(client):
    _class = SchoolClassFactory.create()
    quiz_instance = ClassQuizFactory.create(class_id=_class.id)
    regex = r'^http:\/\/local.*8080\/quiz_view\/([0-9a-z-]*)'
    extracted_uuid = re.findall(regex, quiz_instance.url)[0]

    assert quiz_instance.uuid is not None
    assert re.match(regex, quiz_instance.url) is not None
    assert extracted_uuid == str(quiz_instance.uuid)

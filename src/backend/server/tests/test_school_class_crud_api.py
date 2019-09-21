import json
import unittest

from server.tests.base import BaseTestCase
# , LoggedInTeacherFactory
from server.tests.factories import SchoolClassFactory, TeacherFactory, StudentFactory, ClassQuizFactory
from server.tests.utils import LoggedInUserMixin


class TestSchoolClassCRUDAPI(BaseTestCase):
    @unittest.skip("Temporarily skipped")
    def test_school_class_ping(self):
        with self.client:
            response = self.client.get(
                '/api/v1/school_class/ping'
            )

            data = json.loads(response.data.decode())
            self.assert200(response)
            self.assertEqual(data, {
                "status": "success",
                "message": "Pinged school class"
            })

    def test_get_school_class_with_id(self):
        teacher = TeacherFactory.create()
        student = StudentFactory.create()
        school_class = SchoolClassFactory.build()
        class_quiz = ClassQuizFactory.build()
        class_quiz.class_id = school_class.id
        school_class.quizzes.append(class_quiz)
        school_class.teacher_id = teacher.id
        school_class.student_id = student.id
        school_class.save()
        class_quiz.save()
        with self.client:
            # self.login_with_user(teacher.email, teacher.password, teacher.role)
            # TODO: Fix this test to use logged in user
            with LoggedInUserMixin(teacher.email, teacher.password, teacher.role):
                response = self.client.get(
                    f'/api/v1/school_class/{school_class.id}'
                )
                data = json.loads(response.data)
                self.assert200(response)
                self.assertEqual(data['data']['school_classes'][0], {
                    'name': school_class.name,
                    'subject': school_class.subject,
                    'start_date': str(school_class.start_date)
                })

    @unittest.skip("Temporarily skipped")
    def test_add_school_class(self):
        new_class = SchoolClassFactory.build()
        with self.client:
            response = self.client.post(
                '/api/v1/school_class',
                json=new_class.to_json()
            )
            print(response.data)
            self.assertStatus(response, 201)

    @unittest.skip("Temporarily skipped")
    def test_fetch_school_class_list(self):
        SchoolClassFactory.create_batch(5)
        with self.client:
            response = self.client.get(
                '/api/v1/school_class'
            )
            self.assert200(response)
            data = json.loads(response.data)
            self.assertEqual(len(data['data']['school_classes']), 5)

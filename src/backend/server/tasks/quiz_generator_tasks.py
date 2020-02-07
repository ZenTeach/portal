from server import celery
from server.models import ClassQuiz
from server.lib import QuizGenerator, GoogleFormsGenerator
from server.lib.interfaces.GAppScript import AppScriptInterface
from flask_mail import Message
from celery.utils.log import get_task_logger
import asyncio

from .commons import send_mail, send_mail_with_html

logger = get_task_logger(__name__)

@celery.task
def generate_pdf(quiz_id):
    generator = QuizGenerator("/home/flask/server/server/api/templates",
                                  "demo.html",
                                  "/tmp/zenteach_quizzes")
    try:
        generator.generate(quiz_id)
    except Exception as e:
        print(e)

    return generator.quiz_file_name

async def process_appscript(qid, t_uuid):
    generator = GoogleFormsGenerator("/home/flask/server/server/api/templates",
                                     qid,
                                     "google_form_creator.html")

    try:
        api = AppScriptInterface(t_uuid)
        await api.check_authorization()
        js_file_content = generator.generate()
        gform_id = generator.current_quiz.gform_id
        project_id, dep_id, version = await api.process_request(gform_id, js_file_content)
        logger.info("Project id {}, Deploy id {}, Version {}".format(project_id, dep_id, version))
        generator.update_quiz(project_id, dep_id, version)
        return project_id
    except Exception as e:
        logger.exception(e)
        print(e)

@celery.task
def generate_gform_quiz(quiz_id, teacher_uuid):
    script_id = asyncio.run(process_appscript(quiz_id, teacher_uuid))
    quiz = ClassQuiz.query.filter_by(id=quiz_id).first()
    quiz.script_id = script_id
    quiz.save()
    return script_id

async def async_execute_app_script(scriptId, teacher_uuid):
    try:
        api = AppScriptInterface(teacher_uuid)
        await api.check_authorization()
        result = await api.execute_script(scriptId)
        if 'error' in result:
            error = result['error']['details'][0]
            print("Script error message: {0}".format(error['errorMessage']))

            if 'scriptStackTraceElements' in error:
                print("Script error stacktrace:")
                for trace in error['scriptStackTraceElements']:
                    print("\t{0}: {1}".format(trace['function'],
                        trace['lineNumber']))
        return result['response'].get('result', {})
    except Exception as e:
        logger.exception(e)
        print(e)

@celery.task
def execute_app_script(script_id, teacher_uuid):
    # TODO: Still broken, needs fixing
    url = asyncio.run(async_execute_app_script(script_id, teacher_uuid))
    return url

@celery.task
def send_google_form_email(teacher_email, published_url):
    msg = Message(subject="Your Google Form quiz is ready!")
    msg.recipients=["{}".format(teacher_email)]

    # msg.body = "Hi,\n Your Google Form can be found by following this link: {}\n \nThank you for using zenteach,\n \nZenteach support".format(published_url)
    send_mail_with_html(msg, "google_form_template.html", form_link=published_url)
    #send_mail(msg)

@celery.task
def send_quiz_pdf(teacher_email, quiz_file_dir):
    msg = Message(subject="Hi! Your Quiz have arrived.")
    msg.recipients=["{}".format(teacher_email)]

    with open(quiz_file_dir, 'rb') as fp:
        msg.attach("Quiz.pdf", "application/pdf", fp.read())

    send_mail(msg)

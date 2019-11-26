from server import celery
from server.lib import QuizGenerator

@celery.task
def generate_pdf(quiz):
    generator = QuizGenerator("/home/flask/server/server/api/templates",
                                  "demo.html",
                                  "/home/flask/server/server/api/tmp",
                                  title=quiz.subject + " quiz",
                                  )

    try:
        generator.generate(quiz)
    except Exception as e:
        print(e)

    return generator.quiz_file_name

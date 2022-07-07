from flask.cli import FlaskGroup
from server import create_app, db
from server.lib.tasks.data_tasks import (mark_grades_sent_for_old_quizzes,
                                         trigger_knowledge_item_migration,
                                         trigger_quiz_regrading,
                                         trigger_topic_migration)

app = create_app()


cli = FlaskGroup(create_app=create_app)


@cli.command("recreate_db")
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("truncate_tables")
def truncate_tables():
    def clear_data(session):
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            print(f"Clear table {table}")
            session.execute(table.delete())
        session.commit()

    clear_data(db.session)


@cli.command("migrate_topics")
def migrate_topics():
    """
        migrate_topics: move topics from old table to new table
    """
    trigger_topic_migration()


@cli.command("migrate_knowledgeitems")
def migrate_knowledgeitems():
    """
        migrate_knowledgeitems: move topics from old table to new table
    """
    trigger_knowledge_item_migration()


@cli.command("run_mark_grades_sent_for_old_quizzes")
def run_mark_grades_sent_for_old_quizzes():
    mark_grades_sent_for_old_quizzes()


@cli.command("db_conf")
def db_conf():
    db.configure_mappers()


@cli.command("routes")
def routes():
    """ Prints all registered routes"""
    print("Method \tEndpoint \turl name")
    for rule in app.url_map.iter_rules():
        print("{} \t{} \t{}".format(rule.methods, rule.endpoint, str(rule)))


@cli.command("trigger_quiz_regrading")
def start_quiz_regrading():
    trigger_quiz_regrading()


@cli.command("seed")
def seed():
    from server.models import run_seed

    run_seed()


if __name__ == "__main__":
    cli()

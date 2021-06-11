from flask.cli import FlaskGroup
from flask_migrate import MigrateCommand
from server import create_app, db

app = create_app()
cli = FlaskGroup(create_app=create_app)
cli.add_command("db", MigrateCommand)


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


@cli.command("db_conf")
def db_conf():
    db.configure_mappers()


@cli.command("routes")
def routes():
    """ Prints all registered routes"""
    print("Method \tEndpoint \turl name")
    for rule in app.url_map.iter_rules():
        print("{} \t{} \t{}".format(rule.methods, rule.endpoint, str(rule)))


@cli.command("seed")
def seed():
    from server.models import run_seed

    run_seed()


if __name__ == "__main__":
    cli()

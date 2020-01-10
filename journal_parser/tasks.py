from edutatar.celery import app
from journal_parser.JournalParser.main import execute

@app.task(time_limit=3600)
def exec(data):
    fn = execute(data)
    results = {'file_name': fn}

    return results


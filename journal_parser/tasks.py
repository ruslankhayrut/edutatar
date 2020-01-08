from celery import shared_task
from journal_parser.JournalParser.main import execute

@shared_task
def exec(data):
    fn = execute(data)
    results = {'file_name': fn}

    return results


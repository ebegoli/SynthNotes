from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl import connections, Text, DocType, Date, Keyword, Integer
import psycopg2 as psy
from tqdm import tqdm

class Note(DocType):

    encounter_id = Keyword()
    person_id = Keyword()
    start = Date()
    stop = Date()
    text = Text()


    class Meta:
        index = 'synthea'
        doc_type = 'note'


def _bulk(doc):
    d = doc.to_dict(include_meta=True)
    d['_op_type'] = 'index'
    d['doc'] = d['_source']
    del d['_source']
    return d


def main():
    connections.create_connection(hosts=['172.22.8.180:9200'])
    Note.init()

    def note_stream():
        params = {'database': 'synthea', 'user': 'postgres', 'host': '172.22.10.147'}
        conn = psy.connect(**params)
        cur = conn.cursor()

        cur.execute("""
                    SELECT id, encounter_id, person_id, start, stop, note
                    FROM notes;
        """)

        for (i, eid, pid, start, stop, text) in tqdm(cur):
            yield Note(encounter_id=eid, person_id=pid, start=start,
                     stop=stop, text=text, meta={'id': i})

    print(bulk(connections.get_connection(), (_bulk(n) for n in note_stream()), stats_only=True))


if __name__ == '__main__':
    main()

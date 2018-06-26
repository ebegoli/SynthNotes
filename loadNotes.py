from synthnotes.generators import NoteGenerator
import psycopg2 as psy
from tqdm import tqdm

def main():

    generator = NoteGenerator()

    params = {'database': 'synthea', 'user': 'postgres', 'host': '172.22.8.180'}
    conn = psy.connect(**params)

    cur = conn.cursor("reader")
    curWrite = conn.cursor()
    cur.execute("""select e.id, e.person_id, e.start, e.stop 
                    FROM encounter e
                    LEFT JOIN notes n
                    on e.id = n.encounter_id
                    WHERE e.system = 'SNOMED-CT' 
                        and e.code = '24642003' 
                        and n.encounter_id is NULL;
                """)

    count = 0
    for row in tqdm(cur):
        encounter_id = row[0]
        person_id = row[1]
        start = row[2]
        stop = row[3]
        
        note = generator.generate()
        curWrite.execute("""
            INSERT into notes(encounter_id, person_id, note, start, stop)
            Values (%s, %s, %s, %s, %s)
            """, [encounter_id, person_id, note, start, stop])
        count += 1

    print(f"wrote {count} notes")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()

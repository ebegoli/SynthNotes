from synthnotes.generators import NoteGenerator
import psycopg2 as psy


def main():

    generator = NoteGenerator()

    params = {'database': 'synthea', 'user': 'postgres', 'host': '172.22.10.147'}
    conn = psy.connect(**params)

    cur = conn.cursor()

    cur.execute("""select id, person_id, start, stop from encounter 
                where display like 'Psychiatric procedure or service' limit 10;
                """)
    results = cur.fetchall()

    for row in results:
        encounter_id = row[0]
        person_id = row[1]
        start = row[5]
        stop = row[6]

        note = generator.generate()
        cur.execute("""
            INSERT into notes(encounter_id, person_id, note, start, stop)
            Values (%s, %s, %s, %s)
            """, encounter_id, person_id, note, start, stop)


if __name__ == '__main__':
    main()

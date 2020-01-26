import psycopg2, psycopg2.extras

from .libserver import Response as _Response
from .settings import PSQL_DATABASE, PSQL_HOST, PSQL_PASSWORD, PSQL_SCHEMA, PSQL_USER

# Initialize connection
con = psycopg2.connect(
    database=PSQL_DATABASE,
    user=PSQL_USER,
    password=PSQL_PASSWORD,
    host=PSQL_HOST,
    port="5432",
    options=f"-c search_path={PSQL_SCHEMA}",
)

print(
    f"[Connected to Postgre DB]    postgresql://{PSQL_USER}:{PSQL_PASSWORD}@{PSQL_HOST}:5432/{PSQL_DATABASE}",
)
print(f"[psql] USE SCHEMA {PSQL_SCHEMA};")


def psql(query, params=None):

    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Print query
    if params:
        query = cur.mogrify(query, params).decode("utf-8")
    print(f"[psql] {query}")

    # init result object
    result = PgResult(query)

    #
    # Attempt query
    try:
        cur.execute(query)
        result.set_rows(cur.fetchall())
        # result.rows = cur.fetchall()
        # if len(result.rows):
        #     result.row = result.rows[0]
        con.commit()
        cur.close()

    except psycopg2.Error as err:
        #
        # Log error
        # https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
        print(f"[psql] {err.pgerror}")

        # Roll back
        con.rollback()
        cur.close()

        # Set err_msg
        result.err_msg = err.pgerror

        return result

    #
    # Set return message
    result.msg = cur.statusmessage
    print(f"[psql] {result.msg}")

    return result


class PgResult:
    def __init__(self, query, rows=None, msg=None, err_msg=None):
        """ Defines a convenient result from `psql()` """

        self.query = query

        self.rows = rows
        self.msg = msg

        self.err_msg = err_msg

    @property
    def Response(self):
        """ Used ONLY for ERRORS """

        return _Response(data={"error": self.err_msg}, code=400)

    def set_rows(self, fetchall):

        self.rows = list(map(lambda x: x._index, fetchall))
        if len(self.rows):
            self.row = self.rows[0]

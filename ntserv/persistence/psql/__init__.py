"""Postgres utilities"""
from typing import Union

import psycopg2
import psycopg2.extras
import sanic.response

from ntserv import __db_target_ntdb__
from ntserv.env import PSQL_DATABASE, PSQL_HOST, PSQL_PASSWORD, PSQL_SCHEMA, PSQL_USER
from ntserv.utils.libserver import Response200Success, Response500ServerError
from ntserv.utils.logger import get_logger

_logger = get_logger(__name__)


class PgResult:
    """
    Result object for all in app queries, with handler and helper methods.
    Defines a convenient result for `psql()`,
    """

    def __init__(self, query: str, err_msg: str = str()) -> None:
        self.query = query

        # TODO: do these belong in init or update? Do we pass in rows to __init__ even?
        self.rowcount = 0
        self.row: dict = {}
        self.rows: list = []

        self.msg = str()
        self.err_msg = err_msg

    @property
    def http_response_error(self) -> sanic.response.HTTPResponse:
        """Used ONLY for ERRORS"""

        return Response500ServerError(
            data={"errMsg": "General database error (Postgres)", "stack": self.err_msg}
        )

    # noinspection PyProtectedMember
    def set_rows(self, cur: psycopg2._psycopg.cursor) -> None:
        """Sets the DictCursor rows based on cur.fetchall()"""

        self.rowcount = cur.rowcount
        # WARN: some exception, see below usage of set_rows()
        fetchall = cur.fetchall()

        self.rows = []

        if len(fetchall):
            headers = [x.name for x in cur.description]

            # Build dict from named tuple
            for entry in fetchall:
                row = {}
                # NOTE: assumes len(headers) == len(entry)
                for i, element in enumerate(entry):
                    header = headers[i]
                    row[header] = element
                self.rows.append(row)

            # Set first row
            self.row = self.rows[0]


# noinspection PyProtectedMember
def build_con(
    database: str = PSQL_DATABASE,
    user: str = PSQL_USER,
    password: str = PSQL_PASSWORD,
    host: str = PSQL_HOST,
    port: str = "5432",
    options: str = f"-c search_path={PSQL_SCHEMA}",
    connect_timeout: float = 8,
) -> psycopg2._psycopg.connection:
    """Build and return con"""
    con = psycopg2.connect(
        database=database,
        user=user,
        password=password,
        host=host,
        port=port,
        options=options,
        connect_timeout=connect_timeout,
    )

    _url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    _logger.debug("psql %s", _url)

    return con


def psql(query: str, params: Union[list, tuple, None] = None) -> PgResult:
    """

    @param query: SQL query
    @param params: Optional. Parameters Tuple[], or list of parameters List[tuple]
    @return: PgResult object, with any errors and row(s) populated
    """
    # TODO:  mandatory "RETURNING id" after all "INSERTS"

    # Initialize connection
    try:
        con = build_con()
    except psycopg2.OperationalError as err:
        _logger.error("build_con() failed: %s", repr(err))
        return PgResult(query=str(), err_msg="failed to build con")

    # Build cursor
    try:
        cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except AttributeError as err:
        _logger.error("con.cursor() failed: %s", repr(err))
        return PgResult(query=str(), err_msg="failed to build cursor")

    # Print query (mogrify, if not many)
    if params:
        query = cur.mogrify(query, params).decode("utf-8")  # type: ignore
    _logger.debug("[psql]   %s;", query)

    # init result object
    result = PgResult(query)

    # --------------------------------------------
    # Attempt query
    # --------------------------------------------
    try:
        # TODO: support cur.executemany()
        cur.execute(query)
    except psycopg2.Error as err:
        # https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
        _logger.warning("[psql]   %s", err.pgerror)

        # Set err_msg
        result.err_msg = str(err.pgerror)

        # Roll back
        con.rollback()
        con.close()

        # Return empty result instance
        return result

    # --------------------------------------------
    # Extract result
    # --------------------------------------------
    try:
        result.set_rows(cur)
    except psycopg2.ProgrammingError as err_prog:
        # WARN: err_prog: no results to fetch
        _logger.debug("Extract fetchall / commit failed: %s", repr(err_prog))

    # Commit
    con.commit()
    con.close()

    # Set return message
    result.msg = cur.statusmessage
    _logger.debug("[psql]   %s", result.msg)

    return result


def verify_db_version_compat() -> bool:
    """Returns true if the attached Postgres schema is of target version"""
    # FIXME: use this to verify, e.g. cache reload(), and prior to any SQL operation
    # NOTE: Should this cause any other failures, if version isn't equal?
    pg_result = psql("SELECT * FROM version ORDER BY id DESC LIMIT 1")
    if pg_result.err_msg:
        _logger.warning("PgResult err_msg: %s", pg_result.err_msg)
    return bool(__db_target_ntdb__ == pg_result.row["version"])


def get_pg_version(**kwargs: dict) -> sanic.HTTPResponse:
    """
    Returns current (and previous) Postgres schema versions
        (there's an endpoint for this)
    """
    _ = kwargs

    pg_result = psql("SELECT * FROM version")
    rows = pg_result.rows
    for row in rows:
        row["created"] = row["created"].isoformat()

    return Response200Success(data={"message": pg_result.msg, "versions": rows})

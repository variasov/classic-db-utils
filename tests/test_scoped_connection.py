from classic.db_utils import ScopedConnection, ConnectionPool

import psycopg


def test_scoped_connection():
    pool = ConnectionPool(lambda: psycopg.connect())
    conn = ScopedConnection(pool)



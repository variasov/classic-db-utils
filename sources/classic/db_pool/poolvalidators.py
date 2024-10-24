validators = {}


def validator(conn_type, cls=None):
    def validator(cls):
        validators[conn_type] = cls
        return cls

    if cls:
        validators[conn_type] = cls

    return validator


class ConnectionValidator:
    def validate(self, conn):
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
        except Exception:
            return False
        return True

    def before_release(self, conn):
        conn.rollback()
        return self.validate(conn)


try:
    from psycopg2 import extensions as psycopg2_ext
    from psycopg2.extensions import connection as psycopg2_conn
except ImportError:
    pass
else:

    @validator(psycopg2_conn)
    class Psycopg2ConnectionValidator(ConnectionValidator):
        def validate(self, conn):
            try:
                conn.isolation_level
            except Exception:
                return False
            return True

        def before_release(self, conn):
            if conn.closed:
                return False
            status = conn.info.transaction_status
            if status == psycopg2_ext.TRANSACTION_STATUS_UNKNOWN:
                return False
            elif status != psycopg2_ext.TRANSACTION_STATUS_IDLE:
                conn.rollback()
                return True
            return True


class MysqlConnectionValidator(ConnectionValidator):
    def validate(self, conn):
        try:
            conn.ping()
        except Exception:
            return False
        return True


try:
    from pymysql.connections import Connection as pymysql_conn
except ImportError:
    pass
else:
    validator(pymysql_conn, MysqlConnectionValidator)

try:
    from MySQLdb.connections import Connection as mysqldb_conn
except ImportError:
    pass
else:
    validator(mysqldb_conn, MysqlConnectionValidator)

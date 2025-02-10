'''
    PostgreSQL connection
'''
import psycopg2
from api.utils.config import postgres_user, postgres_password, postgres_db, postgres_host, postgres_port


def connector():
    '''
        Get conn
    '''
    return psycopg2.connect(
        dbname=postgres_db,
        user=postgres_user,
        password=postgres_password,
        host=postgres_host,
        port=postgres_port)


def health():
    '''
        Check healt of the connection
    '''
    try:
        conn = connector()
        closed = conn.closed
        conn.close()
    except psycopg2.OperationalError:
        return False
    return closed == 0


if __name__ == "__main__":
    conn_obj = connector()
    health()
    conn_obj.close()

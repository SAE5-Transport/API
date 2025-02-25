from flask import jsonify
from api.services.postgres import connector

# create a new user


def add_user(user):
    '''
        Add a new user securely
    '''
    conn = connector()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO USERS (IdUser) VALUES (%s)", (user,))
        conn.commit()
    except Exception as e:
        conn.rollback()  # Annule les changements en cas d'erreur
        raise e
    finally:
        cursor.close()
        conn.close()


def getall_user():
    '''
        Get all users in the database
    '''
    conn = connector()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM USERS")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows)  # Transforme en JSON

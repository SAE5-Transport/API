from api.services.postgres import connector


def add_agent(id_user, id_company):
    '''
        Add a new agent after verifying that both the user and the company exist
    '''
    conn = connector()
    cursor = conn.cursor()

    try:
        # Vérifier si l'utilisateur existe
        cursor.execute("SELECT 1 FROM USERS WHERE IdUser = %s", (id_user,))
        if cursor.fetchone() is None:
            return False, "User not found"

        # Vérifier si la compagnie existe
        cursor.execute(
            "SELECT 1 FROM COMPANY WHERE IdCompany = %s", (id_company,))
        if cursor.fetchone() is None:
            return False, "Company not found"

        # Ajouter l'agent
        cursor.execute(
            "INSERT INTO AGENT (IdUser, IdCompany) VALUES (%s, %s)",
            (id_user, id_company)
        )
        conn.commit()
        return True, "Agent added successfully"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cursor.close()
        conn.close()


def get_agents():
    '''
        Get all agents
    '''
    conn = connector()
    cursor = conn.cursor()

    cursor.execute("SELECT IdUser, IdCompany FROM AGENT")
    agents = [{"idUser": row[0], "idCompany": row[1]}
              for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return agents


def delete_agent(id_user, id_company):
    '''
        Delete an agent after verifying if they exist
    '''
    conn = connector()
    cursor = conn.cursor()

    try:
        # Vérifier si l'agent existe
        cursor.execute(
            "SELECT 1 FROM AGENT WHERE IdUser = %s AND IdCompany = %s",
            (id_user, id_company)
        )
        if cursor.fetchone() is None:
            return False, "Agent not found"

        # Supprimer l'agent
        cursor.execute(
            "DELETE FROM AGENT WHERE IdUser = %s AND IdCompany = %s",
            (id_user, id_company)
        )
        conn.commit()
        return True, "Agent deleted successfully"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cursor.close()
        conn.close()


def is_agent(id_user):
    '''
        Check if a user is an agent
    '''
    conn = connector()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT 1 FROM AGENT WHERE IdUser = %s", (id_user,))
        result = cursor.fetchone()
        return result is not None

    except Exception as e:
        return False

    finally:
        cursor.close()
        conn.close()

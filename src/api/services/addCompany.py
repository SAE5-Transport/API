from api.services.postgres import connector


def add_company(id_company, name):
    '''
        Add a new company to the database after checking if it already exists
    '''
    conn = connector()
    cursor = conn.cursor()

    try:
        # Vérifier si la compagnie existe déjà
        cursor.execute(
            "SELECT 1 FROM COMPANY WHERE IdCompany = %s", (id_company,))
        if cursor.fetchone() is not None:
            return False, "Company already exists"

        # Ajouter la compagnie
        print(f"DEBUG: Inserting company {id_company} - {name}")  # Ajout Debug
        cursor.execute(
            "INSERT INTO COMPANY (IdCompany, Name) VALUES (%s, %s)",
            (id_company, name)
        )
        conn.commit()
        return True, "Company added successfully"

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {str(e)}")  # Afficher l'erreur en console
        return False, str(e)

    finally:
        cursor.close()
        conn.close()


def get_companies():
    '''
        Get all companies
    '''
    conn = connector()
    cursor = conn.cursor()

    cursor.execute("SELECT IdCompany, Name FROM COMPANY")
    rows = cursor.fetchall()

    companies = [{"idCompany": row[0], "Name": row[1]} for row in rows]

    print(f"DEBUG: Retrieved companies from DB -> {companies}")  # Ajout Debug

    cursor.close()
    conn.close()
    return companies


def delete_company(id_company):
    '''
        Delete a company after verifying if it exists
    '''
    conn = connector()
    cursor = conn.cursor()

    try:
        # Vérifier si la compagnie existe
        cursor.execute(
            "SELECT 1 FROM COMPANY WHERE IdCompany = %s", (id_company,))
        if cursor.fetchone() is None:
            return False, "Company not found"

        # Supprimer la compagnie
        cursor.execute(
            "DELETE FROM COMPANY WHERE IdCompany = %s", (id_company,))
        conn.commit()
        return True, "Company deleted successfully"

    except Exception as e:
        conn.rollback()
        return False, str(e)

    finally:
        cursor.close()
        conn.close()

from api.services.postgres import connector


# create a new friend
def add_friend(friend, user):
    '''
        Add a new friend (bidirectional)
    '''
    conn = connector()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO friends (IdUser, FriendId) VALUES (%s, %s)", (user, friend))
    cursor.execute(
        "INSERT INTO friends (IdUser, FriendId) VALUES (%s, %s)", (friend, user))
    conn.commit()
    cursor.close()
    conn.close()
    return friend


def get_friends(user):
    '''
        Get all friends of a user
    '''
    conn = connector()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT FriendId FROM friends WHERE IdUser = %s", (user,))
    friends = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return friends


def delete_friend(user, friend):
    '''
        Delete a friend
    '''
    conn = connector()
    cursor = conn.cursor()

    # Conversion explicite pour éviter le mismatch de types
    cursor.execute(
        "DELETE FROM friends WHERE IdUser = %s AND FriendId = %s", (
            user, friend)
    )
    cursor.execute(
        "DELETE FROM friends WHERE IdUser = %s AND FriendId = %s", (
            friend, user)
    )

    conn.commit()
    cursor.close()
    conn.close()
    return friend

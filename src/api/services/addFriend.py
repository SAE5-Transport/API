from api.services.postgres import connector


# create a new friend
def add_friend(friend, user):
    '''
        Add a new friend
    '''
    conn = connector()
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT INTO friends (IdUser,FriendId) VALUES ('{user}', {friend})")
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
        f"SELECT * FROM friends WHERE IdUser = '{user}'")
    friends = cursor.fetchall()
    cursor.close()
    conn.close()
    return friends

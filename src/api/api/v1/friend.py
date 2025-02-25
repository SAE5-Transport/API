from flask import Blueprint, request, jsonify
from api.services.addFriend import add_friend, get_friends

friend_bp = Blueprint("friend", __name__, url_prefix='/friend')


@friend_bp.route('/add', strict_slashes=False, methods=['POST'])
def addFriend():
    '''
        Add a new friend
    '''
    try:
        data = request.get_json()
        if not data or "idUser" not in data or "idFriend" not in data:
            return jsonify({"error": "Missing user or friend"}), 400

        user = data["idUser"]
        friend = data["idFriend"]
        add_friend(user, friend)
        return jsonify({"message": f"Friend {friend} added successfully for user {user}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@friend_bp.route('/list', strict_slashes=False, methods=['GET'])
def getFriends(user):
    '''
        Get all friends of a user
    '''
    try:
        user = request.args.get("idUser")
        if not user:
            return jsonify({"error": "Missing user parameter"}), 400

        friends = get_friends(user)
        return jsonify({"friends": friends}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

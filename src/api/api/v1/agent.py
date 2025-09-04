from apifairy import response, other_responses, arguments, body
from flask import Blueprint, request, jsonify
from flask_marshmallow import Marshmallow
from api.services.addAgent import add_agent, get_agents, delete_agent, is_agent

agent_bp = Blueprint("agent", __name__, url_prefix='/agent')

ma = Marshmallow(agent_bp)


class AgentMessageSuccess(ma.Schema):
    message = ma.String()


class AddAgent(ma.Schema):
    AgentId = ma.String(description="ID of the user")
    idCompany = ma.String(description="ID of the company")


class AgentSchema(ma.Schema):
    AgentSchemaId = ma.String(description="ID of the user")
    idCompany = ma.String(description="ID of the company")


@agent_bp.route('/add', strict_slashes=False, methods=['POST'])
@body(AddAgent)
@response(AgentMessageSuccess, 201)
@other_responses({400: 'User or company not found', 500: 'Internal Error'})
def addAgent(data):
    '''
        Add a new agent
    '''
    try:
        id_user = data["AgentId"]
        id_company = data["idCompany"]

        success, message = add_agent(id_user, id_company)

        if not success:
            return jsonify({"error": message}), 400

        return jsonify({"message": f"Agent {id_user} added successfully to company {id_company}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agent_bp.route('/list', strict_slashes=False, methods=['GET'])
@other_responses({400: 'Missing parameter', 500: 'Internal Error'})
def getAgents():
    '''
        Get all agents
    '''
    try:
        agents = get_agents()
        return jsonify({"agents": agents}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agent_bp.route('/delete/<id_user>/<id_company>', strict_slashes=False, methods=['DELETE'])
@response(AgentMessageSuccess, 200)
@other_responses({400: 'User or company not found', 500: 'Internal Error'})
def deleteAgent(id_user, id_company):
    '''
        Delete an agent
    '''
    try:
        success, message = delete_agent(id_user, id_company)

        if not success:
            return jsonify({"error": message}), 400

        return jsonify({"message": f"Agent {id_user} removed successfully from company {id_company}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@agent_bp.route('/isAgent', strict_slashes=False, methods=['GET'])
@other_responses({400: 'Missing parameter', 500: 'Internal Error'})
def checkIsAgent():
    '''
        Check if a user is an agent
    '''
    try:
        id_user = request.args.get("idUser")
        if not id_user:
            return jsonify({"error": "Missing user parameter"}), 400

        result = is_agent(id_user)
        return jsonify({"isAgent": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

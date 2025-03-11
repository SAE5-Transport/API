from apifairy import response, other_responses, arguments, body
from flask import Blueprint, request, jsonify
from flask_marshmallow import Marshmallow
from api.services.addCompany import add_company, get_companies, delete_company

company_bp = Blueprint("company", __name__, url_prefix='/company')

ma = Marshmallow(company_bp)


class CompanyMessageSuccess(ma.Schema):
    message = ma.String()


class AddCompany(ma.Schema):
    idCompany = ma.String(description="ID of the company")
    AddName = ma.String(description="Name of the company")


class CompanySchema(ma.Schema):
    idCompany = ma.String(description="ID of the company")
    Name = ma.String(description="Name of the company")


@company_bp.route('/add', strict_slashes=False, methods=['POST'])
@body(AddCompany)
@response(CompanyMessageSuccess, 201)
@other_responses({400: 'Company already exists', 500: 'Internal Error'})
def addCompany(data):
    '''
        Add a new company
    '''
    try:
        id_company = data["idCompany"]
        name = data["AddName"]

        success, message = add_company(id_company, name)

        if not success:
            return jsonify({"error": message}), 400

        return jsonify({"message": f"Company {name} added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/list', strict_slashes=False, methods=['GET'])
@other_responses({400: 'Missing parameter', 500: 'Internal Error'})
def getAllCompanies():
    '''
        Get all companies
    '''
    try:
        companies = get_companies()
        return jsonify({"companies": companies}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@company_bp.route('/delete/<id_company>', strict_slashes=False, methods=['DELETE'])
@response(CompanyMessageSuccess, 200)
@other_responses({400: 'Company not found', 500: 'Internal Error'})
def deleteCompany(id_company):
    '''
        Delete a company
    '''
    try:
        success, message = delete_company(id_company)

        if not success:
            return jsonify({"error": message}), 400

        return jsonify({"message": f"Company {id_company} removed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

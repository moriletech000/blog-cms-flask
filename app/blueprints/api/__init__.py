from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint('api', __name__)

# Initialize Flask-RESTX
api = Api(
    api_bp,
    version='1.0',
    title='Blog CMS API',
    description='A comprehensive blog management system API',
    doc='/docs/',
    prefix='/api/v1'
)
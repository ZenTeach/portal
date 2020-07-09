from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from flask import Blueprint, jsonify, make_response, render_template, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Api, Resource
from server.models import Teacher, TeacherSchema
from server.models.oauth2_grants import authorization, require_oauth

oauth_api_blueprint = Blueprint("oauth", __name__)
api = Api(oauth_api_blueprint)


class OAuth2Authorize(Resource):
    def get_user(self):
        user = get_jwt_identity()["identity"]
        return Teacher.query.filter_by(email=user["email"]).first()

    @jwt_required
    def get(self):
        user = self.get_user()
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            # TODO: Send errors correctly
            return error.error
        # TODO: Change this
        return render_template('authorize.html', user=user, grant=grant)

    @jwt_required
    def post(self):
        user = self.get_user()
        confirmation = request.get_json()["confirmation"]

        if confirmation == "Yes":
            grant_user = user
        else:
            grant_user = None
        response = authorization.create_authorization_response(grant_user=grant_user)
        return make_response(response)


class OAuth2Token(Resource):
    def post(self):
        response = authorization.create_token_response()
        return make_response(response)


class OAuth2Revoke(Resource):
    def post(self):
        response = authorization.create_endpoint_response('revocation')
        return make_response(response)


class OAuth2Profile(Resource):
    @require_oauth('profile')
    def get(self):
        teacher_dumper = TeacherSchema()
        teacher = current_token.user
        return make_response(jsonify({"user": teacher_dumper.dump(teacher)}))


api.add_resource(OAuth2Authorize, "/authorize")
api.add_resource(OAuth2Token, "/token")
api.add_resource(OAuth2Revoke, "/revoke")

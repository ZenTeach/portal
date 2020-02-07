"""
API interface to Google App-Script API

Handles Authorization and service discovery
"""
from __future__ import print_function
import pickle
import json
import os
import os.path as path
from server import redis_store
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from asyncio import sleep
from oauth2client import client
import httplib2

DEFAULT_SCOPE = [
    "https://www.googleapis.com/auth/script.projects",
    "https://www.googleapis.com/auth/script.projects.readonly",
    "https://www.googleapis.com/auth/script.deployments",
    "https://www.googleapis.com/auth/script.deployments.readonly",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
    "https://www.googleapis.com/auth/forms",
    "https://www.googleapis.com/auth/forms.currentonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.scripts",
    "https://www.googleapis.com/auth/script.external_request"
    ]

DEFAULT_MANIFEST = '''
{
    "timeZone": "Europe/Berlin",
    "oauthScopes": [
        "https://www.googleapis.com/auth/script.projects",
        "https://www.googleapis.com/auth/script.projects.readonly",
        "https://www.googleapis.com/auth/script.deployments",
        "https://www.googleapis.com/auth/script.deployments.readonly",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
        "https://www.googleapis.com/auth/forms",
        "https://www.googleapis.com/auth/forms.currentonly",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.scripts",
        "https://www.googleapis.com/auth/script.external_request"
    ],
    "dependencies": {
    },
    "exceptionLogging": "STACKDRIVER",
    "executionApi": {
        "access": "ANYONE"
    }
}
'''.strip()

class AppScriptInterface():
    def __init__(self, tid, api_scope=DEFAULT_SCOPE, api_manifest=DEFAULT_MANIFEST):
        """ Constructor.
        Args:

        """
        self.tid = tid
        self.api_scope = api_scope
        self.api_manifest = api_manifest
        self.credentials = None
        self.service = None
        # await self.check_authorization(tid)

    async def check_authorization(self):
        auth_key = "gauth-code_{}".format(self.tid)
        auth_code = redis_store.get(auth_key)
        await sleep(1)
        auth_cred_key = "gauth-credential_{}".format(self.tid)
        cred_blob = redis_store.get(auth_cred_key)
        await sleep(1)
        if cred_blob is None:
            credentials_dir = path.join(os.getcwd(), "server", "lib/interfaces/client_id.json")
            print("auth code", auth_code)
            # flow = Flow.from_client_secrets_file(
            #             credentials_dir,
            #             scopes=[
            #                 "https://www.googleapis.com/auth/script.projects",
            #                 "https://www.googleapis.com/auth/script.projects.readonly",
            #                 "https://www.googleapis.com/auth/script.deployments",
            #                 "https://www.googleapis.com/auth/script.deployments.readonly",
            #                 "https://www.googleapis.com/auth/userinfo.profile",
            #                 "https://www.googleapis.com/auth/userinfo.email",
            #                 "openid",
            #                 "https://www.googleapis.com/auth/forms",
            #                 "https://www.googleapis.com/auth/forms.currentonly"
            #                 "https://www.googleapis.com/auth/drive",
            #                 "https://www.googleapis.com/auth/drive.scripts",
            #                 "https://www.googleapis.com/auth/script.external_request"
            #             ])
            # flow.redirect_uri = 'postmessage'
            # flow.fetch_token(code=auth_code)
            self.credentials = client.credentials_from_clientsecrets_and_code(
                        credentials_dir, self.api_scope, auth_code)
            cred_blob = pickle.dumps(self.credentials)
            redis_store.set(auth_cred_key, cred_blob)
        else:
            self.credentials = pickle.loads(cred_blob)

        # if not self.credentials.access_token_expired:
        #     self.credentials.refresh(httplib2.Http())
        #     await sleep(1)
        http_auth = self.credentials.authorize(httplib2.Http())

        print("credentials: {}", self.credentials)
        # await sleep(1)
        self.service = await self.build_service(self.credentials)

    @classmethod
    async def build_service(self, creds):
        await sleep(1)
        return build('script', 'v1', http=creds)

    def version(self):
        pass

    async def get_version(self, script_id, version_number):
        res = None
        try:
            res = self.service.projects().versions().get(scriptId=script_id, versionNumber=version_number).execute()
            await sleep(1)
            return res
        except errors.HttpError as error:
            print(error)
            return False

    async def create_version(self, version, script_id):
        payload = {
            "versionNumber": version,
            "scriptId": script_id,
        }

        res = self.service.projects().versions().create(scriptId=script_id, body=payload).execute()
        await sleep(1)
        return res

    async def execute_script(self, script_id):
        payload = {
            'function': 'createQuiz',
        }

        res = self.service.scripts().run(scriptId=script_id, body=payload).execute()
        await sleep(1)
        return res

    def deploy_script(self, project_id, script_content):
        payload = {
            'files': [{
                'name': 'quiz_creator',
                'type': 'SERVER_JS',
                'source': script_content
            }, {
                'name': 'appsscript',
                'type': 'JSON',
                'source': self.api_manifest
            }]
        }

        res = self.service.projects().updateContent(
            body=payload,
            scriptId=project_id).execute()
        return res


    async def create_deployment(self, project_id, version_number):
        payload = {
            "manifestFileName": "appsscript",
            "versionNumber": version_number,
            "description": "Quiz Generator deployment",
        }
        res = self.service.projects().deployments().create(scriptId=project_id, body=payload).execute()
        await sleep(1)
        return res

    async def get_deployment(self, project_id, deployment_id):
        res = None
        try:
            res = self.service.projects().deployments().get(scriptId=project_id,
                                    deploymentId=deployment_id).execute()
            await sleep(1)
            return res
        except errors.HttpError as error:
            print(error)
            return False

    async def get_project(self, project_id):
        res = None
        try:
            res = self.service.projects().get(scriptId=project_id).execute()
            await sleep(1)
            return res
        except errors.HttpError as error:
            print(error)
            return False

    def create_project(self, title="Sample Quiz Generator Script"):
        request_payload = {
            'title': title
        }

        return self.service.projects().create(body=request_payload).execute()

    async def update_deployment(self, script_id, deployment_id, version_number):
        deployment_config = {
            "versionNumber": version_number,
        }

        res = None
        try:
            res = self.service.projects().deployments().update(scriptId=script_id, deploymentId=deployment_id, body=deployment_config).execute()
            await sleep(1)
            return res
        except Exception as e:
            print(e)

    async def process_request(self, gform_id, script_content):
        """
            Handles creation of quiz forms on Google Form
            Args:
                gform_id - identifier in the form of {pid:'...', 'dep_id': '...', 'version': '...'}
        """
        pid = ""
        depid = ""
        version = 0
        if gform_id:
            identity = json.loads(gform_id)
            pid = identity["pid"]
            depid = identity["dep_id"]
            version = int(identity["version"])

        project = None
        if pid != "":
            project = await self.get_project(pid)
            await sleep(1)

        if not project:
            project = self.create_project()
            await sleep(1)

        self.deploy_script(project['scriptId'], script_content)
        await sleep(1)

        version_ = None
        if version != 0:
            version_ = await self.get_version(project['scriptId'], version)

        if version_ is None:
            version_ = await self.create_version(1, project['scriptId'])

        deployment = None
        deployment_id = None
        if depid == "":
            deployment = await self.create_deployment(project["scriptId"], version_["versionNumber"])
            deployment_id = deployment["deploymentId"]
        else:
            deployment = await self.get_deployment(project['scriptId'], depid)
            deployment_id = depid


        print("project", project)
        print("deployment", deployment)
        print("version", version_)
        # deployment_config = deployment["deployments"][0]["deploymentConfig"]
        # await sleep(3)
        # execution_result = await self.execute_script(project['scriptId'])
        # Gform_published_url = None
        # if 'error' in execution_result:
        #     error = execution_result['error']['details'][0]
        #     print("Script error message: {0}".format(error['errorMessage']))

        #     if 'scriptStackTraceElements' in error:
        #         print("Script error stacktrace:")
        #         for trace in error['scriptStackTraceElements']:
        #             print("\t{0}: {1}".format(trace['function'],
        #                 trace['lineNumber']))
        # else:
        #     published_url = execution_result['response'].get('result', {})
        #     Gform_published_url = published_url
        #     print("Google Form Published Url: {}".format(published_url))

        # print(execution_result)
        return (project["scriptId"], deployment_id, version_["versionNumber"])

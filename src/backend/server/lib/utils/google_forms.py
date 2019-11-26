

"""
Shows basic usage of the Apps Script API.
Call the Apps Script API to create a new script project, upload a file to the
project, and log the script's URL to the user.
"""
from __future__ import print_function
import pickle
import os.path
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/script.projects']
SCOPES = [
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/forms.currentonly',
]

SAMPLE_CODE = '''
function helloWorld() {
  console.log("Hello, world!");
}
'''.strip()

SAMPLE_MANIFEST = '''
{
  "timeZone": "America/New_York",
  "exceptionLogging": "CLOUD"
}
'''.strip()

def main():
    """Calls the Apps Script API.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('script', 'v1', credentials=creds)

    # Call the Apps Script API
    try:
        # Create a new project
        request = {'title': 'My Script'}
        response = service.projects().create(body=request).execute()

        # Upload two files to the project
        request = {
            'files': [{
                'name': 'hello',
                'type': 'SERVER_JS',
                'source': SAMPLE_CODE
            }, {
                'name': 'appsscript',
                'type': 'JSON',
                'source': SAMPLE_MANIFEST
            }]
        }
        response = service.projects().updateContent(
            body=request,
            scriptId=response['scriptId']).execute()
        print('https://script.google.com/d/' + response['scriptId'] + '/edit')
    except errors.HttpError as error:
        # The API encountered a problem.
        print(error.content)


class GoogleFormsGenerator(object):
    def __init__(self, auth_scopes, quiz_name, js_tmpl, credentials, output_file, manifest_file):
        """
            Args:
                auth_scopes: list of authorization scopes
                js_tmpl: Javascript template file
                credentials: A credentials json file
                output_file: Pickle serialized output file location
                manifest_file: The manifest file directory
        """
        self.auth_scopes = auth_scopes
        self.js_tmpl = js_tmpl
        self.quiz_name = quiz_name
        self.credentials = credentials
        self.output_file = output_file
        self.manifest = self.load_from_file(manifest_file)

    @classmethod
    def load_from_file(self, file):
        absolute_manifest_file = os.path.join(os.path.realpath(__file__), file)
        if not os.path.exists(absolute_manifest_file):
            raise FileNotFoundError("Manifest file doesn't exist")

        return pickle.load(open(absolute_manifest_file, "rb").read())


    @classmethod
    def load_from_tmpl(self):
        pass

    @classmethod
    def check_authorization(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.output_file):
            with open(self.output_file, 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials, self.auth_scopes)
                creds = flow.run_local_server(port=0)

            with open(self.output_file, 'wb') as token:
                pickle.dump(creds, token)

    def generate(self):
        service = build('script', 'v1', credentials=creds)

        try:
            request = {'title': self.quiz_name}
            response = service.projects().create(body=request).execute()

            app_script = self.load_from_tmpl(self.js_tmpl)
            # Upload two files to the project
            request = {
                'files': [{
                    'name': 'hello',
                    'type': 'SERVER_JS',
                    'source': app_script
                }, {
                    'name': 'appsscript',
                    'type': 'JSON',
                    'source': self.manifest_file
                }]
            }
            response = service.projects().updateContent(
                body=request,
                scriptId=response['scriptId']).execute()

            print('https://script.google.com/d/' + response['scriptId'] + '/edit')
        except errors.HttpError as error:
            # The API encountered a problem.
            print(error.content)


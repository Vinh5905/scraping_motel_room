import webbrowser
import msal

MS_GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'

def get_access_token(application_id, client_secret, scopes):
    client = msal.ConfidentialClientApplication(
        client_id=application_id,
        client_credential=client_secret,
        authority='https://login.microsoftonline.com/consumers/'
    )

    auth_request_url = client.get_authorization_request_url(scopes)
    print(auth_request_url)
    webbrowser.open(auth_request_url)

    authorization_code = input('Enter the authorization code: ')

    token_response = client.acquire_token_by_authorization_code(
        code=authorization_code,
        scopes=scopes
    )

    if 'access_token' in token_response:
        return token_response['access_token']
    else:
        raise Exception('Failed to acquire access token: ' + str(token_response))
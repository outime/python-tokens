import json
import os
import requests
import time

ONE_YEAR = 3600*24*365

CONFIG = {'url': os.environ.get('OAUTH_ACCESS_TOKEN_URL'),
          'dir': os.environ.get('CREDENTIALS_DIR')}

TOKENS = {}


def init_fixed_tokens_from_env():
    env_val = os.environ.get('OAUTH2_ACCESS_TOKENS', '')
    for part in env_val.split(','):
        key, sep, val = part.partition('=')
        TOKENS[key] = {'access_token': val, 'expires_at': time.time() + ONE_YEAR}


def configure(**kwargs):
    CONFIG.update(kwargs)


def manage(token_name, scopes):
    TOKENS[token_name] = {'scopes': scopes}
    init_fixed_tokens_from_env()


def start():
    # TODO: start background thread to manage tokens
    pass


def get(token_name):
    token = TOKENS[token_name]
    access_token = token.get('access_token')
    if not access_token or time.time() > token['expires_at'] - 20*60:
        path = CONFIG['dir']
        with open(os.path.join(path, 'user.json')) as fd:
            user_data = json.load(fd)
        with open(os.path.join(path, 'client.json')) as fd:
            client_data = json.load(fd)
        body = {
                'grant_type': 'password',
                'username': user_data.get('application_username'),
                'password': user_data.get('application_password'),
                'scope': ' '.join(token['scopes'])
                }

        r = requests.post(CONFIG['url'], data=body,
                          auth=(client_data.get('client_id'), client_data.get('client_secret')))
        r.raise_for_status()
        data = r.json()
        token['data'] = data
        token['expires_at'] = time.time() + data.get('expires_in')
        token['access_token'] = data.get('access_token')

    access_token = token.get('access_token')
    return access_token

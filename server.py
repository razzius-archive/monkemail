import os
import urlparse

from flask import Flask, make_response, redirect, request

import requests
from github import Github


GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

GITHUB_OAUTH_ENDPOINT = 'https://github.com/login/oauth/access_token'

app = Flask('Monkemail')

def get_primary_github_email(github_client):
    """Get a Github user's primary email."""
    user_emails = github_client.get_user().get_emails()

    for email_dict in user_emails:
        __import__('ipdb').set_trace()
        if email_dict['primary']:
            return email_dict['email']

    # Return the first email if none are primary
    return user_emails[0]['email']

@app.route('/oauth')
def oauth():
    """Request an API access token from Github.

    Redirect to the homepage with a cookie."""
    #TODO Use state for security

    payload = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': request.args['code'],
        'state': request.args['state'],
    }

    github_request = requests.post(GITHUB_OAUTH_ENDPOINT, data=payload)

    querystring = github_request.text
    credentials = dict(urlparse.parse_qsl(querystring))
    token = credentials['access_token']

    # Now that we have their token, we can instantiate a Github client

    github = Github(token)
    user_email = get_primary_github_email(github)

    redirect_url = 'http://monkemail.me/login'

    response = make_response(redirect(redirect_url))
    response.set_cookie('github_api_token', token)
    response.set_cookie('user_email', user_email)

    return response

if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 8000))

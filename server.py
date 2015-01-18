import os
import urlparse
import urllib

from flask import Flask, make_response, redirect, request
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

import requests
from github import Github
from mandrill import Mandrill


MANDRILL_API_KEY = os.environ.get('MANDRILL_API_KEY')
mandrill_client = Mandrill(MANDRILL_API_KEY)

GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

GITHUB_OAUTH_ENDPOINT = 'https://github.com/login/oauth/access_token'

app = Flask('Monkemail')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']


### Database Bizness ###
db = SQLAlchemy(app)


class BaseMixin(object):
    """Defines an id column and default tablename for database models."""
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(self):
        """ Set default tablename."""
        return self.__name__.lower()


class User(db.Model, BaseMixin):
    """Represents a user who has signed up for this service using their Github."""
    email = Column(String(120), unique=True)
    github_api_token = Column(String(50), unique=True)

    def __init__(self, email, github_api_token):
        self.email = email
        self.github_api_token = github_api_token



class Website(db.Model, BaseMixin):
    """Represents a website that a user owns which can be integrated with Monkemail."""
    contact_email = Column(String(120), unique=True)
    url = Column(String(255))
    owner_id = Column(Integer, ForeignKey('user.id'), index=True)
    owner = relationship('User', foreign_keys=[owner_id])


def get_primary_github_email(github_client):
    """Get a Github user's primary email."""
    user_emails = github_client.get_user().get_emails()

    for email_dict in user_emails:
        if email_dict['primary']:
            return email_dict['email']

    # Return the first email if none are primary
    return user_emails[0]['email']

@app.route('/')
def test():
    """Endpoint to see if the service is working."""
    return 'success'

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

    # Save the user

    new_user = User(user_email, token)
    db.session.add(new_user)

    try:
        db.session.commit()
    except IntegrityError:
        # They're already in the database
        pass

    session_data = {
        'github_api_token': token,
        'user_email': user_email
    }
    redirect_url = 'http://monkemail.me/login?{}'.format(urllib.urlencode(session_data))

    return redirect(redirect_url)

@app.cli.command()
def initdb():
    db.create_all()

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=int(os.environ.get('PORT', 5000)))

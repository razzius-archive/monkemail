import os
import urlparse
import urllib

from flask import Flask, abort, jsonify, redirect, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask_cors import CORS

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import NoResultFound

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

cors = CORS(app)


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

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email
        }



class Website(db.Model, BaseMixin):
    """Represents a website that a user owns which can be integrated with Monkemail."""
    contact_email = Column(String(120), unique=True)
    url = Column(String(255))
    owner_id = Column(Integer, ForeignKey('user.id'), index=True)
    owner = relationship('User', foreign_keys=[owner_id])

    def to_json(self):
        return {
            'id': self.id,
            'url': self.url,
            'owner': self.owner.to_json(),
            'contact_email': self.contact_email
        }


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

@app.route('/websites/', methods=['POST'])
def create_website():
    """Create a website for integrating monkemail."""
    request_data = request.get_json()
    user_email = request_data.get('email', None)
    user_github_token = request_data.get('github_api_token', None)
    if not user_email or not user_github_token:
        return 'Need to pass email and github_api_token', 403

    try:
        user = db.session.query(User).filter_by(email=user_email).one()
    except NoResultFound:
        return 'User not found', 404

    if user.github_api_token != user_github_token:
        return 'Authentication data did not match', 403

    website_url = request_data.get('url', None)
    if not website_url:
        return 'Need to specify website url', 400

    website = Website(
        contact_email=user.email,
        owner_id=user.id,
        url=website_url
    )
    db.session.add(website)
    try:
        db.session.commit()
        return jsonify(website.to_json())
    except IntegrityError:
        return 'Already created', 400

@app.route('/websites/', methods=['GET'])
def get_websites():
    """Return a user's registered websites."""
    user_email = request.args.get('email', None)
    user_github_token = request.args.get('github_api_token', None)
    if not user_email or not user_github_token:
        return 'Need to pass email and github_api_token', 403

    try:
        user = db.session.query(User).filter_by(email=user_email).one()
    except NoResultFound:
        return 'User not found', 404

    if user.github_api_token != user_github_token:
        return 'Authentication data did not match', 403

    websites = db.session.query(Website).join(Website.owner).filter_by(id=user.id).all()

    return jsonify({
        'length': len(websites),
        'data': [
            website.to_json() for website in websites
        ]
    })

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

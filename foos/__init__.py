# -*- coding: utf-8 -*-
from collections import OrderedDict
from urllib import urlencode
import os

from flask import Flask, redirect, request
import requests

from pylexa.app import alexa_blueprint, handle_launch_request
from pylexa.intent import handle_intent
from pylexa.response import (
    AlexaResponseWrapper, LinkAccountCard, PlainTextSpeech, Response, SimpleCard
)


app = Flask(__name__)
app.register_blueprint(alexa_blueprint)
app.response_class = AlexaResponseWrapper

AWS_VENDOR_ID = os.getenv('AWS_VENDOR_ID')
SLACK_CLIENT_ID = os.getenv('SLACK_CLIENT_ID')
SLACK_CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL', 'botstuff')


@app.before_request
def log_request_json():
    print request.headers
    print request.json


@handle_launch_request
def handle_launch(request):
    return PlainTextSpeech('Launching')


@handle_intent('AMAZON.HelpIntent')
def handle_help(request):
    card = SimpleCard(title='Help title', content='This is stuff you can do')
    speech = PlainTextSpeech('This will surely help')
    return Response(speech=speech, card=card)


@handle_intent('IsGood')
def handle_IsGood_intent(request):
    name = request.slots['Someone']
    message = 'I think {} is pretty good at foosball'.format(name)
    if name.lower() == 'jeff':
        message = "I can't believe how bad {} is at foosball. It's embarassing to watch".format(name)
    elif name.lower() == 'patrick':
        message = 'We are all blessed to witness such a great talent'
    speech = PlainTextSpeech(message)
    return Response(speech=speech)


@handle_intent('Echo')
def handle_echo_intent(request):
    return PlainTextSpeech(request.slots.get('message', 'Nothing to echo'))


@handle_intent('MoreFoos')
def handle_MoreFoos_intent(request):
    if not request.access_token:
        return Response(
            speech=PlainTextSpeech('You must sign in first'),
            card=LinkAccountCard(),
        )
    else:
        token = request.access_token
        text = request.slots.get('message', 'This is a test')
        url = 'https://slack.com/api/chat.postMessage'
        res = requests.post(url, {
            'token': request.access_token,
            'channel': SLACK_CHANNEL,
            'text': text,
            'as_user': False,
            'username': 'Benevolent Robot Foosball Overlord',
        })
        if res.json()['ok']:
            return PlainTextSpeech("Reinforcements are on the way!")
        else:
            return PlainTextSpeech('Oops, something went wrong.')


@handle_intent('unrecognized_intent')
def handle_unrecognized_intent(request):
    return PlainTextSpeech("I'm sorry I didn't understand that")


states = []

def make_redirect_uri():
    client_id = request.args.get('client_id')
    scope = request.args.get('scope')
    state = request.args.get('state')
    url = 'https://slack.com/oauth/authorize'
    query_string = urlencode(OrderedDict(
        scope=scope,
        state=state,
        client_id=client_id
    ))
    return '{}?{}'.format(url, query_string)


@app.route('/oauth/entry')
def oauth_entry_point():
    state = request.args.get('state')
    states.append(state)
    return redirect(make_redirect_uri())


@app.route('/oauth/redirect')
def oauth_redirect():
    state = request.args.get('state')
    code = request.args.get('code')

    response = requests.get(
        'https://slack.com/api/oauth.access?{}'.format(urlencode({ 'code': code })),
        auth=(SLACK_CLIENT_ID, SLACK_CLIENT_SECRET)
    )
    response_json = response.json()
    if 'bot' in response_json:
        access_token = response_json['bot'].get('bot_access_token')
    else:
        access_token = response_json['access_token']

    redirect_url = 'https://pitangui.amazon.com/spa/skill/account-linking-status.html?vendorId={}'.format(AWS_VENDOR_ID)
    redirect_url += '#{}'.format(urlencode({'access_token': access_token, 'state': state, 'token_type': 'Bearer'}))
    return redirect(redirect_url)


if __name__ == '__main__':
    app.run(debug=True)

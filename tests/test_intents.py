# -*- coding: utf-8 -*-
import json
import mock
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from foos import app


class _AlexaTestCase(unittest.TestCase):

    def input(self):
        raise NotImplementedError('You must implement the input method')

    def output(self):
        raise NotImplementedError('You must implement the expected output method')

    def should_return_expected_output(self):
        with app.test_client() as client:
            rv = client.post('/', data=json.dumps(self.input()), headers={'content-type': 'application/json'})
            self.assertEqual(json.loads(rv.get_data()), self.output())


class _IntentTestCase(_AlexaTestCase):

    access_token = None

    def intent_name(self):
        raise NotImplementedError('You must set the intent name')

    def slots(self):
        raise NotImplementedError('You must set the slot values')

    def input(self):
        slots = {
            slot['name']: slot
            for slot in self.slots()
        }
        user = {
            'userId': 'amzn1.ask.account.USER_ID'
        }
        if self.access_token:
            user['accessToken'] = self.access_token
        return {
            "request": {
                "intent": {
                    "name": self.intent_name(),
                    "slots": slots
                },
                "requestId": "EdwRequestId.REQUEST_ID",
                "timestamp": "2016-04-14T19:31:51Z",
                "type": "IntentRequest"
            },
            "session": {
                "application": {
                    "applicationId": "amzn1.echo-sdk-ams.app.APPLICATION_ID"
                },
                "attributes": None,
                "new": True,
                "sessionId": "SessionId",
                "user": user
            },
            "version": "1.0"
        }


class TestIsGoodIntentWithBestPlayer(_IntentTestCase):

    def intent_name(self):
        return 'IsGood'

    def slots(self):
        return [{
            'name': 'Someone',
            'value': 'Patrick'
        }]

    def output(self):
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "We are all blessed to witness such a great talent"
                },
                "shouldEndSession": True
            }
        }

class TestIsGoodIntentWithWorstPlayer(_IntentTestCase):

    def intent_name(self):
        return 'IsGood'

    def slots(self):
        return [{
            'name': 'Someone',
            'value': 'Jeff'
        }]

    def output(self):
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "I can't believe how bad Jeff is at foosball. It's embarassing to watch"
                },
                "shouldEndSession": True
            }
        }


class TestHelpIntent(_IntentTestCase):

    def intent_name(self):
        return 'AMAZON.HelpIntent'

    def slots(self):
        return [{ 'name': 'message' }]

    def output(self):
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "This will surely help"
                },
                "card": {
                    "type": "Simple",
                    "title": "Help title",
                    "content": "This is stuff you can do"
                },
                "shouldEndSession": True
            }
        }


class TestMoreFoosIntentWithoutAccessToken(_IntentTestCase):

    def intent_name(self):
        return 'MoreFoos'

    def slots(self):
        return []

    def output(self):
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "You must sign in first"
                },
                "card": {
                    "type": "LinkAccount",
                },
                "shouldEndSession": True
            }
        }



class _BaseMoreFoosIntentWithAccessTokenTestCase(_IntentTestCase):

    access_token = 'DEADBEEF'

    def setUp(self):
        self.patcher = mock.patch('foos.requests')
        mocker = self.patcher.start()
        mocker.post.return_value.json.return_value = { 'ok': self.success }

    def tearDown(self):
        self.patcher.stop()

    def intent_name(self):
        return 'MoreFoos'

    def slots(self):
        return []


class WhenPostToSlackSucceeds(_BaseMoreFoosIntentWithAccessTokenTestCase):

    success = True

    def output(self):
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Reinforcements are on the way!"
                },
                "shouldEndSession": True
            }
        }


class WhenPostToSlackSucceed(_BaseMoreFoosIntentWithAccessTokenTestCase):

    success = False

    def output(self):
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Oops, something went wrong."
                },
                "shouldEndSession": True
            }
        }


class TestLaunchRequest(_AlexaTestCase):

    def input(self):
        return {
            "request": {
                "locale": "en-US",
                "requestId": "EdwRequestId",
                "timestamp": "2016-04-19T14:28:53Z",
                "type": "LaunchRequest"
            },
            "session": {
                "application": {
                    "applicationId": "amzn1.echo-sdk-ams.app.app_id"
                },
                "new": True,
                "sessionId": "SessionId.session_id",
                "user": {
                    "userId": "amzn1.ask.account.user_id"
                }
            },
            "version": "1.0"
        }

    def output(self):
        return {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                "type": "PlainText",
                "text": "Launching"
                },
                "shouldEndSession": True
            }
        }

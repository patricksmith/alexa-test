## Test Alexa application

This is a simple app for Alexa to see how integration with Alexa works.

### Development

Install requirements using:

```bash
pip install -r requirements.txt
```

Then, the Flask server can be run using:

```bash
python foos/__init__.py
```

The server will then be running on `localhost:5000`.


### Testing

To test, first install the dev requirements:

```bash
pip install -r dev-requirements.txt
```

Then, tests can be run using the `nosetests` command.


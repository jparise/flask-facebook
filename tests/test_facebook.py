import unittest

from flask import Flask
from flask_facebook import Facebook

class InitializationTests(unittest.TestCase):

    def test_deferred_initialization(self):
        self.assertIsNone(Facebook().app)

    def test_missing_values(self):
        app = Flask(__name__)
        self.assertRaises(AssertionError, Facebook, app)

        app.config['FACEBOOK_APP_ID'] = '123'
        app.config['FACEBOOK_APP_SECRET'] = '456'
        self.assertEqual(Facebook(app).app, app)

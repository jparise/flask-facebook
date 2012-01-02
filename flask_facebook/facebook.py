# Flask-Facebook
# Copyright (c) 2012 Jon Parise <jon@indelible.org>

"""Adds Facebook support to a Flask application"""

from __future__ import absolute_import
import facebook

from flask import abort, request, _request_ctx_stack
from functools import wraps

__author__ = 'Jon Parise <jon@indelible.org>'
__version__ = '0.10'

class FacebookSession(object):
    """An authenticated Facebook user session."""

    def __init__(self, uid, access_token, expires=None):
        self.uid = uid
        self.access_token = access_token
        self.expires = expires
        self.graph = facebook.GraphAPI(access_token)

    def __repr__(self):
        return '<%s uid=%s, expires=%s>' % \
                (self.__class__.__name__, self.uid, self.expires)

class Facebook(object):
    """This class provides a Facebook interface.

    The ``FACEBOOK_APP_ID`` and ``FACEBOOK_APP_SECRET`` configuration
    variables must be set.
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

        self.unauthorized_callback = None

    def __repr__(self):
        app_id = self.app.config.get('FACEBOOK_APP_ID', '(none)')
        return '<%s app_id=%s>' % (self.__class__.__name__, app_id)

    def init_app(self, app):
        """Initialize the Facebook interface for the given application."""
        self.app = app

        # These two configuration variables must be set; there is no
        # reasonable default value we can use for either of them.
        assert 'FACEBOOK_APP_ID' in  self.app.config, \
            'FACEBOOK_APP_ID configuration variable must be set'
        assert 'FACEBOOK_APP_SECRET' in  self.app.config, \
            'FACEBOOK_APP_SECRET configuration variable must be set'

        # Register either our debug or normal request processor.
        if 'FACEBOOK_DEBUG_UID' in self.app.config:
            self.app.before_request(self._before_request_debug)
        else:
            self.app.before_request(self._before_request)

    def unauthorized_handler(self, callback):
        self.unauthorized_callback = callback

    def _before_request(self):
        # Look for an active Facebook user session.
        user = self._get_cookie_user() or self._get_canvas_user()

        # If the user is currently logged into Facebook, 'user' will be a
        # dictionary containing the session information.
        if user is not None:
            ctx = _request_ctx_stack.top
            ctx.facebook = FacebookSession(user['uid'], user['access_token'],
                                           user.get('expires', None))

    def _before_request_debug(self):
        # Explicitly create a Facebook session using our debug values.
        ctx = _request_ctx_stack.top
        ctx.facebook = FacebookSession(self.app.config['FACEBOOK_DEBUG_UID'],
                                       self.app.config['FACEBOOK_DEBUG_TOKEN'])

    def _get_cookie_user(self):
        """Attempt to get the Facebook user from a cookie."""
        try:
            app_id = self.app.config['FACEBOOK_APP_ID']
            app_secret = self.app.config['FACEBOOK_APP_SECRET']
            return facebook.get_user_from_cookie(request.cookies,
                                                 app_id, app_secret)
        except facebook.GraphAPIError as e:
            self.app.logger.error("Facebook Error: %s" % e)
            return None

    def _get_canvas_user(self):
        """Attempt to get the Facebook user from a canvas signed_request."""
        signed_request = request.form.get('signed_request', None)
        if signed_request is not None:
            try:
                app_secret = self.app.config['FACEBOOK_APP_SECRET']
                data = facebook.parse_signed_request(signed_request, app_secret)
            except facebook.GraphAPIError as e:
                self.app.logger.error("Facebook Error: %s" % e)
                return None

            if data and 'user_id' in data:
                return dict(uid=data['user_id'],
                            access_token=data['oauth_token'])
        return None

    @property
    def session(self):
        """Get the current Facebook session object."""
        ctx = _request_ctx_stack.top
        if ctx is not None:
            return getattr(ctx, 'facebook', None)

    @property
    def graph(self):
        """Get the GraphAPI object for the current Facebook session."""
        session = self.session
        if session is not None:
            return session.graph

    def required(self, func):
        """View decorator that enforces a Facebook session requirement.

        If there isn't an active Facebook session, the unauthorized handler
        is run.  If an unauthorized handler was not configured, an HTTP 401
        Unauthorized response is sent.
        """
        @wraps(func)
        def decorated(*args, **kwargs):
            if self.session is None:
                # If we have an unauthorized callback, defer to it.
                if self.unauthorized_callback is not None:
                    return self.unauthorized_callback()
                # Otherwise, abort with an HTTP Unauthorized response.
                abort(401)
            return func(*args, **kwargs)
        return decorated

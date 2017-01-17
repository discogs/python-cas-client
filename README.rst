python-cas-client
=================

A Python CAS (Central Authentication Service) client for interfacing with a CAS
service implementation, such as https://github.com/rbCAS/CASino or
https://github.com/apereo/cas.

This project provides tools for building well-formed CAS-related URLs, parsing
CAS XML payloads and managing the server-side session stores necessary for
handling SLO (single logout).

Installation
------------

Supports Python 2.7 and 3.4.

::

    $ git clone git@github.com:discogs/python-cas-client.git
    $ cd python-cas-client
    python-cas-client$ pip install .
    ...

Testing
-------

``cas_client`` uses ``tox`` to run its unit tests under Python 2.7 and 3.4.

::

    python-cas-client$ tox

Example
-------

The following un-tested pseudo-code shows how you might use ``cas_client`` in a
Flask project.

::

    from cas_client import CASClient
    from flask import Flask, redirect, request, session, url_for

    app = Flask(__name__)

    app_login_url = 'http://www.my-app.com/login'
    cas_url = 'http://cas.my-app.com'
    cas_client = CASClient(cas_url, auth_prefix='')

    @app.route('/login')
    def login():
        ticket = request.args.get('ticket')
        if ticket:
            try:
                cas_response = cas_client.perform_service_validate(
                    ticket=ticket,
                    service_url=app_login_url,
                    )
            except:
                # CAS server is currently broken, try again later.
                return redirect(url_for('root'))
            if cas_response and cas_response.success:
                session['logged-in'] = True
                return redirect(url_for('root'))
        del(session['logged-in'])
        cas_login_url = cas_client.get_login_url(service_url=app_login_url)
        return redirect(cas_login_url)

    @app.route('/logout')
    def logout():
        del(session['logged-in'])
        cas_logout_url = cas_client.get_logout_url(service_url=app_login_url)
        return redirect(cas_logout_url)

    @app.route('/')
    def root():
        if session.get('logged-in'):
            return 'You Are Logged In'
        else:
            return 'You Are Not Logged In'

This pseudo-code does not handle server-side session stores or single logout,
only the bare minimum for standard login and logout.

Liana
=====

Bootstraped with [djng](https://github.com/djng/djng)

Prerequisites
-------------

 * Installed [Python](http://python.org/) and [Virtualenv](http://pypi.python.org/pypi/virtualenv) in a unix-style environment.
   See this [guide](http://install.python-guide.org/) for guidance.
 * An installed version of [Postgres](http://www.postgresql.org/) to test locally.
   Also create a user and database for your project.
 * Installed [Node.js](http://nodejs.org/).
 * Installed [Grunt](http://gruntjs.com/getting-started) and [Bower](http://bower.io/#install-bower).
 * Installed [Compass](http://compass-style.org/install/).
 * Installed [postgresql](http://www.postgresql.org/)
 * Optional [elasticsearch](https://www.elastic.co/)

Developing
----------
Watch for changes in your client:

    cd client
    grunt watch

Run the django development server:

    source venv/bin/activate
    cd server
    python manage.py runserver_plus

#####AngularJs Client

All client dependencies are managed by npm and bower:

    cd client
    npm install
    bower install

###Serving static assets

All static assets are served by [WhiteNoise](http://whitenoise.evans.io/en/latest/) in production to keep things simple.
During local development the files are served by the [django.contrib.staticfile](https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#module-django.contrib.staticfiles)
app directly from the client directory.

**Note:** As this is a SPA Django needs to catch all URLs handled by the client and return the index.html.
Therefore this URL pattern has to come last in your `urls.py` as it would otherwise override all other url definitions.
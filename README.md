Liana
=====

Bootstrapped with [djng](https://github.com/djng/djng)

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

Crawling
--------

    source venv/bin/activate
    cd server
    python manage.py crawl_shops -f ottos,galaxus -s 100


Elastic Search
--------------

    EXPORT ELASTIC_SSL_URL=https://user:pw@domain.com

    source venv/bin/activate
    cd server
    python manage.py rebuild_index
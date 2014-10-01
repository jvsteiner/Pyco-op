# Pyco-op

1. Clone repo:

    $ git clone https://github.com/jvsteiner/Pyco-op.git

2. Change directory:

    $ cd pyco-op

3. Install dependencies:

    $ pip install -r requirements.txt

4. Copy the example email config and edit the values, use env.py in production to override development settings:

    $ cp env/email.py.example env/email.py

    $ cp env/env.py.example env/env.py

5. Initialize, migrate and upgrade the database:

    $ mkdir tmp

    $ python app.py db migrate

    $ python app.py db upgrade

5. Start the app:

    $ python app.py runserver

NOTE: layout.html uses a _scripts.html helper that references several javascript libraries that are dependancies for the UI:

twitter bootstrap 3.2.0

jquery 1.8.2

knockout.js 2.2.1

knockout mapping plugin

knockout-bootstrap 0.2.1

jquery.csv 0.71

The helper is set to use a CDN link when config.PRODUCTION == True, and serve from /static otherwise.  You will need to obtain local copies to work in development mode.

To create an initial user, populate the config/email.py with working smtp details, then signup.
use the admin interface at localhost:5000/admin to add an admin role, and grant it to your user.
You can then swap out the is_accessible definitions in the admin views to prevent non-admin users from acessing the admin interface. You will also need to use the admin interface to create roles called "farmer", "buyer", and "manager": most likely assigning all of them to your initial user.

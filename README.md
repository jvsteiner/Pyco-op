# Pyco-op

1. Clone repo:

    $ git clone https://github.com/jvsteiner/Pyco-op.git

2. Change directory:

    $ cd pyco-op

3. Install dependencies: instructions for virtualenv not included - you are using virtualenv, right?

    $ pip install -r requirements.txt

4. Copy the example email config and edit the values, use env.py in production to override development settings: If you use a capistrano style deployment technique like fabistrano, you will need to put the env/ tmp/ and static/ directories in the shared directory structure. 

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

colResizable 1.3

The helper is set to use a CDN link when config.PRODUCTION == True, and serve from /static otherwise.  You will need to obtain local copies to work in development mode. You can use:

    $ chmod u+x getjs.sh 

    $ ./getjs.sh

To create an initial user, populate the config/email.py with working smtp details, then signup.
use the admin interface at localhost:5000/admin to add an admin role, and grant it to your user.
You can then swap out the is_accessible definitions in the admin views to prevent non-admin users from acessing the admin interface. You will also need to use the admin interface to create roles called "farmer", "buyer", and "manager": most likely assigning all of them to your initial user.

The MIT License (MIT)

Copyright (c) 2015 Jamie Steiner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

This is my submission to implement your code challenge (an account manager with an API to create accounts and transactions, where transactions can be deposit/withdrawal/transfer, and the transfer can be in the same currency or in different currency, in which case a live currency exchange rate will be applied; with error checking in all operations)
It's done in Django and Python3.

2-june-2017 Daniel Clemente Laboreo. n142857@gmail.com, http://www.danielclemente.com/


Instructions to run it:

1. Create a virtualenv:

virtualenv env
source env/bin/activate


2. Install requirements
pip3 install -r requirements.txt


3. Delete db.sqlite3 and create a new database if you want. If you use mine (which has some test transactions), you'll be able to log in to admin with: dc:password_set_in_admin


4. ./manage.py runserver   and visit http://127.0.0.1:8000/


5. Use the code inside scripts/api_client_calls.sh to test the API client. Change parameters manually


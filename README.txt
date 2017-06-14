This is my submission to implement your code challenge (an account manager with an API to create accounts and transactions, where transactions can be deposit/withdrawal/transfer, and the transfer can be in the same currency or in different currency, in which case a live currency exchange rate will be applied; with error checking in all operations)
It's done in Django and Python3.

2-june-2017 Daniel Clemente Laboreo. n142857@gmail.com, http://www.danielclemente.com/


Notes for viewers:
- there were no requirements for UI so it's very basic. Most operations are run through a command-line API
- there were no requirements for tests, so I did only manual tests. Ideally I would have done a program to recheck consistency in all DB objects (by checking all rules in every object, in a loop), and also unit tests in tests.py (start from scratch, create some conditions, check results). That's what I did in other projects and I can show you code. In this project I kept myself to the requirements (which were already estimated at 2 or 3 days work, which is rather long for a coding challenge)
- there were no requirements about coding style, so I wrote it in I style I like. My validator runs and combines epylint+pyflakes+pep8 but discards many PEP8 opinions; e.g. I find long lines totally acceptable, and I don't care much about whitespace as long as it's consistent. I am very strict about readable and well documented code, but I don't follow PEP8 by default; but if you tell me to, I will
- there's few commented code, e.g. some "# print(…)"., it's harmless, scarce and can help you to debug it; it's left there by choice. I also know that in real life you shouldn't commit a sqlite3 database into git; but in this case it's practical (you don't need to start from scratch)
- I think it's safe and there are no bugs, but didn't do an exhaustive test
- I coded this in GNU Emacs, while using features like git integration, time tracking (org-mode) and code snippets (org-babel)


Instructions to run it:

1. Create a virtualenv:

virtualenv env
source env/bin/activate


2. Install requirements
pip3 install -r requirements.txt


3. Delete db.sqlite3 and create a new database if you want. If you use mine (which has some test transactions), you'll be able to log in to admin with: dc:password_set_in_admin


4. ./manage.py runserver   and visit http://127.0.0.1:8000/


5. Use the code inside scripts/api_client_calls.sh to test the API client. Change parameters manually


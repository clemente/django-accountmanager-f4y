
echo "Creating an account:"

# no password
# curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"currency": "CHF" }' 'http://localhost:8000/api/accounts/?format=json'

echo "(if it fails, create ApiKey in admin)"
# dc is my user
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey dc:password_set_in_admin" -X POST --data '{"currency": "CHF" }' 'http://localhost:8000/api/accounts/?format=json'

echo "Press enter to continue creating transactions"
read continue

echo "Creating transactions:"
#  curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey dc:password_set_in_admin" -X POST --data '{"destAccount": "12355565", "sourceAccount": null }' 'http://localhost:8000/api/transactions/?format=json'
echo Deposit:
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey dc:password_set_in_admin" -X POST --data '{"destAccount": "12355566", "sourceAccount": null, "amount": 51 }' 'http://localhost:8000/api/transactions/?format=json'
echo Transfer:
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey dc:password_set_in_admin" -X POST --data '{"destAccount": "12355565", "sourceAccount": "12355565", "amount": 51 }' 'http://localhost:8000/api/transactions/?format=json'
echo Withdrawal:
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey dc:password_set_in_admin" -X POST --data '{"destAccount": null, "sourceAccount": "12355565", "amount": 51 }' 'http://localhost:8000/api/transactions/?format=json'

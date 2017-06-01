
echo "Creating an account:"

# no password
# curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"currency": "CHF" }' 'http://localhost:8000/api/account/?format=json'

echo "(if it fails, create ApiKey in admin)"
# dc is my user
curl --dump-header - -H "Content-Type: application/json" -H "Authorization: ApiKey dc:password_set_in_admin" -X POST --data '{"currency": "CHF" }' 'http://localhost:8000/api/account/?format=json'


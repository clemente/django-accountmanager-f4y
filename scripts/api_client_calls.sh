
echo "Creating an account:"
curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"currency": "CHF" }' 'http://localhost:8000/api/account/?format=json'

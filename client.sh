curl -X DELETE \
  -H "Content-type: application/json" \
  -d '{"n":3, "hostnames": ["server1"]}' \
  "http://0.0.0.0:5000/rm"

echo ""
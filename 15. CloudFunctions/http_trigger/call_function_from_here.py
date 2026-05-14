from requests import post

r = post('https://europe-west8-pcloud2026.cloudfunctions.net/hello_http',json={'name':'matteo'})
print(r.status_code)
print(r.text)


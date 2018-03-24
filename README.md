# AUFM Web App

## REST API

Below are the endpoints to whcih the REST API will respond. Note that all PUT
and POST requests must content type `application/json`

### Users

- `/api/user`
  - Methods: GET, POST (not yet implemented)

### Parts

- `/api/part`
  - Methods: GET, POST
  - Actions:
    - __GET__: Returns all the parts in the system, as a list of JSON objects
    - __POST__:
- `/api/part/<element_id>`
  - Methods: GET, PUT, DELETE
- `api/part/<element_id>/protocol`
  - Methods: GET
- `api/part/<element_id>/protocol/<protocol_id>`
  - Methods: POST, DELETE


### Protocols

- `/api/protocol`
  - Methods: GET, POST
- `/api/protocol/<protocol_id>`
  - Methods: GET, PUT, DELETE

### Buildings

- `/api/building`
  - Methods: GET, POST
- `/api/building/<name_or_id>`
  - Methods: GET, PUT, DELETE


### Protocol Families

- `/api/protocol-family`
  - Methods: GET, POST
- `/api/protocol-family/<family_id>`
  - Methods: GET, PUT, DELETE
- `/api/protocol-family/<family_id>/protocol/<protocol_id>`
  - Methods: POST, DELETE

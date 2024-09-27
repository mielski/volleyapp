
## Dependencies

This project uses pipenv

### installing dependencies locally

- create a virtual env based on pipenv
- open command prompt
- `pip install pipenv`
- `pipenv install`

## setup environment

This application requires a mongodb server as backend.
The connection to this server should be stored in the environment variable MONGO_SERVER

### using docker

- install docker for desktop
- run the command `docker run -p 27017:27017 --name mongo_trainings --pull missing mongo:latest `
- set the environment MONGO_SERVER=localhost:27017


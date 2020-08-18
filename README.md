# Radius Server in Pythong using PyRad  

This repo contains the Radius Server used  by Spotipo for authenticating Guests in Hotspots.

It's based on the awesome https://github.com/pyradius/pyrad 


## How to run the server

Server can be deployed using docker-compose, just execute. 

```shell script
docker-compose build
docker-compose up
```

Docker is pre-configured with a NAS and a Radius user for easy testing.

## Testing Server
Script will create,both accounting and authentication end points running on ports 1812 and 1813 resp.

### Authentication Test

```shell script
python tests/test_auth.py
```

### Accounting  Test

```shell script
python tests/test_accounting.py
```


## Development

Server is based on Gevent and needs to be ported to asyncio-uvloop

Below are the main files that can be checked.

- server.py : Main Entry point
- access_handler.py : Handles Access Requests
- accounting_handler.py : Handles Accounting Requests

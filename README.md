# Implementation Details

All components can be started via `main.py`. I've used the Python package `argparse` in order to parse command line arguments passed to this file.

The main file can be started in two modes:

- In Client mode the following arguments apply:
  - `-m 1` indicates `main.py` is invoked in client (Charging Point) mode; in this mode the CP itself and a REST API are started
  - `-cpid` is used in order to pass the charge point identifier
  - `-cids` is used in order to pass connector ids as a list of comma separated integeres (e.g `-cids 1,2,3`)
  - `-op` is used to pass the remote ocppp port to which the client is connecting, by default this is 9000
  - `-ap` is used to pass the local port on which the REST API server is started
  - `-u` is used to pass the username
  - `-p` is used to pass the password; for brevity purposes the password is not masked
  
- In Server mode the following apply
  - `-m 1` indicates `main.py` is invoked in client (Charging Point) mode; in this mode the CP itself and a REST API are started
  - `-cpid` is used in order to pass the charge point identifier
  - `-op` is used to pass the local ocppp port on which the ocpp server is listening
  - `-u` is used to pass the username
  - `-p` is used to pass the password; for brevity purposes the password is not masked

Example usages: 

`python main.py -m 1 -cpid 10 -cids 1,2 -op 9000 -ap 8080 -u username -p password` - for client components (CP + REST API)
`python main.py -m 2 -op 9000 -u username -p password` - for server component (OCPP Server)

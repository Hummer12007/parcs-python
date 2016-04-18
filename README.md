# PARCS Python

## Installation

### Linux (Fedora)
1. Install python2, virtualenv
2. Create virtual environment with: ```virtualenv -p python2 py2-env``` and activate it: ```source py2-env/bin/activate```
3. Install dependencies with pip: netifaces pyro4, py-cpuinfo, requests, flask

### Linux (Ubuntu)
Run ubuntu_install.sh

### Vagrant on any environment
1. Install vagrant
2. Use ```vagrant up master (worker1)``` to get fully configured ubuntu box with PARCS Python
3. Use ```vagrant ssh master (worker1)``` to connect to the box.

## Running

### Use start.py

IP is an optional parameter. Use it in case network_utils.py#get_ip unable to detect IP.

#### Config file mode
```python2 start.py -config /path_to_config/conf.config```

Config file examples:

Master:
```
[Node]
master=True
port=8080
```

Worker:
```
[Node]
master=False
port=8090
[Master Node]
ip=localhost
port=8080
```

#### Command line arguments
Use ```python2 start.py -h``` for help


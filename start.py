#!/usr/bin/env python2.7
from parcs_py import parcs, Config
import argparse

parser = argparse.ArgumentParser(description='PARCS Python launcher...')
parser.add_argument('-ip', help='Node ip')
parser.add_argument('-port', help='Node port')
parser.add_argument('-master_ip', help='Master node IP')
parser.add_argument('-master_port', help='Master node port')
parser.add_argument('-config', help='Configuration file location')

args = parser.parse_args()
config = None
if args.config is None:
    ip = args.ip
    port = int(args.port) if args.port else None
    master_ip = args.master_ip
    master_port = int(args.master_port) if args.master_port else None
    config = Config(ip, port, master_ip, master_port)
else:
    config = Config.load_from_file(args.config)

parcs.start(config)

import parcs_py
from parcs_py import app, Config
import argparse

parser = argparse.ArgumentParser(description='PARCS Python launcher...')
parser.add_argument('-port', help='Node port')
parser.add_argument('-job_home', help='Directory with job files')
parser.add_argument('-master_ip', help='Master node IP')
parser.add_argument('-master_port', help='Master node port')
parser.add_argument('-config', help='Configuration file location')

args = parser.parse_args()
config = Config.load_from_file(args.config) if args.config is not None else Config(int(args.port), args.job_home,
                                                                                   args.master_ip,
                                                                                   int(args.master_port))
app.start(config)

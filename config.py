import yaml

with open("config.yml") as file:
    cfg = yaml.load(file)

HOST = cfg['api_server']['host']
PORT = cfg['api_server']['port']
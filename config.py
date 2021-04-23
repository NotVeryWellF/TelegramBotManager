import yaml

with open("config.yml") as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)

HOST = cfg['api_server']['host']
PORT = cfg['api_server']['port']
JWT_SECRET = cfg['jwt']['secret']
JWT_ALGORITHM = cfg['jwt']['algorithm']
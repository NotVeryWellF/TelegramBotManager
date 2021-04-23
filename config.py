import yaml
import logging

with open("config.yml") as file:
    cfg = yaml.load(file, Loader=yaml.FullLoader)

HOST = cfg['api_server']['host']
PORT = cfg['api_server']['port']
JWT_SECRET = cfg['jwt']['secret']
JWT_ALGORITHM = cfg['jwt']['algorithm']

try:
    EXPIRY = int(cfg['jwt']['expiry_days'])*24*60*60 + int(cfg['jwt']['expiry_hours'])*60*60 +\
             int(cfg['jwt']['expiry_minutes'])*60 + int(cfg['jwt']['expiry_seconds'])
except:
    EXPIRY = 600
    logging.warning('Expiry time in config.yml is not correct, using default value = 600s.')

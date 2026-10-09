import json
import secrets

CONFIG_FILE = '.conf'

class Version:
    """
    1.  Version du projet (réécriture complette = usless ou fin de cycle de dev (ex : version stable utilisable avec tableau de score (private joke)))
    2.  Ajout / Modification majeur d'un mechanisme (ex : gamemode / mode / etc)
    3.  Ajour / Modification d'un mechanisme (ex : modification du calcule du score)
    4.  Patch micro-modification / patch d'erreur (ex : modification d'un texte)
    """
    VERSION: str
    DATE: str
    PATCH_NOTES: str

    def __init__(self):
        # need to make somthing more robust than this, but for now it will do the job
        with open('VERSION', 'r') as f:
            lines = f.readlines()
            self.config = {}
            comment_area = False
            for line in lines:
                if comment_area:
                    if line.strip() == '"""':
                        comment_area = False
                    continue
                if line.strip() and not line.startswith('#'):
                    if line.strip().startswith('"""'):
                        comment_area = True
                        continue
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    self.config[key.strip()] = value.strip()
            self.set_params()

    def set_params(self):
        self.VERSION = self.config.get('VERSION', 'X.X.X.X')
        self.DATE = self.config.get('DATE', 'xx-xx-xxxx')
        self.PATCH_NOTES = self.config.get('PATCH_NOTES', 'N/A')


class Config:

    DB_FORMAT: str
    DB_NAME: str
    DB_HOST: int
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    #DEFAULT_USER: str
    #DEFAULT_USER_PASSWD: str

    APP_SECRET: str

    CLEANUP_INTERVAL: int
    CHALLENGE_TTL: int
    

    HOST: str = '0.0.0.0'
    PORT: int = 8080

    LOCATIONS_FILE: str = 'locations.json'
    VERSION: Version = Version()

    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            if config_file.endswith('.json'):
                self.config = json.load(f)
            if config_file.endswith('.conf'):
                self.config = {}
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        self.config[key.strip()] = value.strip()
            self.set_params()

    def set_params(self):

        self.DB_FORMAT = self.config.get('DB_FORMAT', 'sqlite')
        self.DB_NAME = self.config.get('DB_NAME', 'local_db')
        self.DB_HOST = self.config.get('DB_HOST', None)
        self.DB_PORT = int(self.config.get('DB_PORT')) if self.config.get('DB_PORT') != '' else None
        self.DB_USER = self.config.get('DB_USER', None)
        self.DB_PASSWORD = self.config.get('DB_PASSWORD', None)

        #self.DEFAULT_USER = self.config.get('DEFAULT_USER', 'admin')
        #self.DEFAULT_USER_PASSWD = self.config.get('DEFAULT_USER_PASSWD', 'admin')

        self.APP_SECRET = self.config.get('APP_SECRET') if self.config.get('APP_SECRET') != "" else secrets.token_hex(16)
        self.CLEANUP_INTERVAL = int(self.config.get('CLEANUP_INTERVAL', 60))
        self.CHALLENGE_TTL = int(self.config.get('CHALLENGE_TTL', 3))

        self.HOST = self.config.get('HOST', '0.0.0.0')
        self.PORT = int(self.config.get('PORT', 8080))

        self.LOCATIONS_FILE = self.config.get('LOCATIONS_FILE', 'locations.json')

config = Config(CONFIG_FILE)
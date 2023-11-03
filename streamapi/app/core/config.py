import pathlib

from starlette.config import Config

ROOT = pathlib.Path(__file__).resolve().parent.parent  # app/
BASE_DIR = ROOT.parent  # ./

#config = Config(BASE_DIR / ".env")

DB_NAME = "streampulseback"    #config("DB_NAME",str)
ATLAS_URI = "mongodb://root:streampulserootpassword@91.186.199.220:27017"  #config("ATLAS_URI",str)

# API_USERNAME = config("API_USERNAME", str)
# API_PASSWORD = config("API_PASSWORD", str)

# Auth configs.
MASTER_API_SECRET_KEY = '123'  #config("MASTER_API_SECRET_KEY", str)
API_SECRET_KEY = ''     #config("API_SECRET_KEY",str)
# API_ALGORITHM = config("API_ALGORITHM", str)
# API_ACCESS_TOKEN_EXPIRE_MINUTES = config(
#     "API_ACCESS_TOKEN_EXPIRE_MINUTES", int
# )  # infinity

REDIS_ARQ_HOST = '91.186.199.220'
REDIS_ARQ_PORT = 6379
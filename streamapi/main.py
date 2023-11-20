from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from aiocache import SimpleMemoryCache

from app.routes import views, service
from app.db.database import DB
from app.core.arq import RedisPool
from app.core.cache import Cache

app = FastAPI()
db = DB()
cache = Cache()
redis_pool = RedisPool()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event('startup')
async def startup():
    db.connect()
    await cache.open()
    await redis_pool.init_pool()    

@app.on_event('shutdown')
async def shutdown():
    db.close()
    await cache.close()
    await redis_pool.close_pool()


app.include_router(views.router)
app.include_router(service.router)
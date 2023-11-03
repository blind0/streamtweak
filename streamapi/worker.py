import asyncio
from arq import cron

from app.core.arq import REDIS_ARQ_SETTINGS, startup, shutdown, start_twitch, pingpong


FUNCTIONS: list = [start_twitch]
CRON_JOBS: list = [
    cron(pingpong,minute=1)
    ]

class WorkerSettings:
    """
    Settings for the ARQ worker.
    """
    job_timeout = 99999999
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = REDIS_ARQ_SETTINGS
    functions: list = FUNCTIONS
    #cron_jobs = CRON_JOBS
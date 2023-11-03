from app.services.viewer_service.app import Application
import logging
import asyncio

def main():
    username = 'one2i67'
    proxy_filepath = 'work_proxies.txt'
    oauth_filepath = 'work_tokens.txt'
    logging.basicConfig(
        filename='log.txt',
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)
    app = Application(username, proxy_filepath,oauth_filepath)
    asyncio.run(app.run())


if __name__ == "__main__":
    main()

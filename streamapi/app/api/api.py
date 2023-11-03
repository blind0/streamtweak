import secrets


async def get_token() -> str:
    token = secrets.token_hex(16)
    return token
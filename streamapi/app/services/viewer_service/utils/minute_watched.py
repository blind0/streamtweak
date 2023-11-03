from base64 import b64encode
import json

async def get_minute_watched_payload(channel_id:str,broadcast_id:str,device_id:str,user_id:str) -> dict:
    event_properties = {
        "channel_id": channel_id,
        "broadcast_id": broadcast_id,
        "player": "site",
        "device_id": device_id,
        "bornuser":True,
        "user_id": user_id,
    }
    minute_watched = [
        {"event": "minute-watched", "properties": event_properties}]
    json_event = json.dumps(minute_watched, separators=(',', ':'))
    after_base64 = (b64encode(json_event.encode("utf-8"))).decode("utf-8")
    return {"data":after_base64}
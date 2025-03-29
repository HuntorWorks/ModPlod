import asyncio

def run_async_tasks(coroutine):
    try: 
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

def print_debug(message):
    print(f"DEBUG: {message}")

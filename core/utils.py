import asyncio
import os
from rich import print

def run_async_tasks(coroutine):
    """Run an async task and return its result"""
    # For a new event loop
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        
        # Check if the loop is running
        if loop.is_running():
            # For a running loop, we need to use a new thread
            import threading
            import concurrent.futures
            
            # Create a new event loop in a new thread
            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(coroutine)
            
            # Run in a thread pool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_new_loop)
                return future.result(timeout=30)  # 30 second timeout
        else:
            # If the loop exists but isn't running, use it
            return loop.run_until_complete(coroutine)
    except RuntimeError:
        # No event loop, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)
    

def get_str_from_args(args: list):
    return " ".join(args)
 
class mp_print:
    def __init__(self):
        pass

    def debug(message):
        if os.getenv("DEBUG"):
            print(f"[purple][ModPlod-DEBUG][/purple]: {message}")
        else:
            pass

    def info(message):
        print(f"[bright_yellow][ModPlod-INFO][/bright_yellow]: {message}")

    def warning(message):
        print(f"[orange3][ModPlod-WARNING][/orange3]: {message}")

    def sys_message(message):
        print(f"[bright_green][ModPlod AI][/bright_green]: {message}")

    def error(message):
        print(f"[red][ModPlod-ERROR][/red]: {message}")

    def mic_input(message):
        print(f"[bright_cyan][ModPlod-INPUT][/bright_cyan][white]:[/white][bright_cyan] {message}")

    def ai_response(message):
        print(f"[blue1][ModPlod-OUTPUT][/blue1][white]:[/white][blue1] {message}")

    def recording_mic_bold(message):
        print(f"[bright_green][ModPlod AI][/bright_green][white]:[white italic bold]Recording...[/white italic bold]")



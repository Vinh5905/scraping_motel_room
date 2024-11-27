import os
import threading

# Get terminal size -> print more beautiful :>
terminal_width = os.get_terminal_size().columns

lock_data = threading.Lock()
lock_previous_crawl = threading.Lock()
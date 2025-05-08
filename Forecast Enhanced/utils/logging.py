# File: utils/logging.py

from datetime import datetime
import pytz

tz_local = pytz.timezone('Europe/Rome')

def log(msg):
    now = datetime.now(tz_local).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}] {msg}")

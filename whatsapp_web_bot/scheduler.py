from apscheduler.schedulers.background import BackgroundScheduler
from polls import send_daily_polls
from attendance import update_attendance
from pdf_generator import generate_pdf
from driver import get_driver
import time

scheduler = BackgroundScheduler()

scheduler.add_job(send_daily_polls, 'cron', hour=20, minute=0)
scheduler.add_job(update_attendance, 'cron', hour=8, minute=0)
scheduler.add_job(generate_pdf, 'cron', hour=8, minute=0)

scheduler.start()

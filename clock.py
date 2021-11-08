from apscheduler.schedulers.blocking import BlockingScheduler
from app import report_elements

sched = BlockingScheduler()


@sched.scheduled_job('interval', days=1)
def timed_job():
    report_elements()


sched.start()


""" from apscheduler.schedulers.background import BackgroundScheduler
from app import report_elements

scheduler = BackgroundScheduler()

# @sched.scheduled_job('interval', minutes=1)
# def timed_job():
scheduler.add_job(func=report_elements, trigger="interval", seconds=120)


scheduler.start() """

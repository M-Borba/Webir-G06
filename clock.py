from apscheduler.schedulers.blocking import BlockingScheduler
from app import report_elements

sched = BlockingScheduler()


@sched.scheduled_job('interval', days=1)
def timed_job():
    report_elements()


sched.start()

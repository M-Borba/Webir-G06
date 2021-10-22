from apscheduler.schedulers.blocking import BlockingScheduler
import app

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=3)
def timed_job():
    app.report_elements()


sched.start()

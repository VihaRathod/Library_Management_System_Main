from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import settings
from jobs.overdue_reminder_job import overdue_reminder_job


scheduler = BackgroundScheduler()


def start_scheduler():

    scheduler.add_job(
        overdue_reminder_job,
        trigger=CronTrigger(
            hour=settings.overdue_reminder_hour,
            minute=settings.overdue_reminder_minute
        ),
        id="overdue_reminder_job",
        replace_existing=True
    )

    scheduler.start()

    print(
        "Scheduler started."
    )

    print(
        f"Overdue reminder scheduled at "
        f"{settings.overdue_reminder_hour:02d}:"
        f"{settings.overdue_reminder_minute:02d}"
    )


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown()

        print(
            "Scheduler stopped."
        )
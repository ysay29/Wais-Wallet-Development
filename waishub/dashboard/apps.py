from django.apps import AppConfig

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        from apscheduler.schedulers.background import BackgroundScheduler
        from dashboard.tasks import send_transaction_reminders
        import atexit

        scheduler = BackgroundScheduler()
        scheduler.add_job(send_transaction_reminders, 'cron', minute='*')  # Every minute
        scheduler.start()

        # Stop scheduler on shutdown
        atexit.register(lambda: scheduler.shutdown(wait=False))


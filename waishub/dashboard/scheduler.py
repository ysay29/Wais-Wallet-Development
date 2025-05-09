from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import send_transaction_reminders

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run send_transaction_reminders every minute
    scheduler.add_job(send_transaction_reminders, 'interval', minutes=1)
    
    scheduler.start()

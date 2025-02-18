from celery.schedules import crontab

app.conf.beat_schedule = {
    'check_network_every_5_minutes': {
        'task': 'alerts.tasks.check_network_status',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
}

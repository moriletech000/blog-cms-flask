from celery.schedules import crontab

# Celery configuration
broker_url = 'redis://redis:6379/0'
result_backend = 'redis://redis:6379/1'

# Task serialization
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Task routing
task_routes = {
    'app.tasks.email.*': {'queue': 'email'},
    'app.tasks.images.*': {'queue': 'images'},
}

# Worker configuration
worker_prefetch_multiplier = 1
task_acks_late = True
worker_max_tasks_per_child = 1000

# Beat schedule for periodic tasks
beat_schedule = {
    # Flush view counters from Redis to PostgreSQL every hour
    'flush-view-counters': {
        'task': 'app.tasks.maintenance.flush_view_counters',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },
    
    # Clean up expired sessions every day at 2 AM
    'cleanup-expired-sessions': {
        'task': 'app.tasks.maintenance.cleanup_expired_sessions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
    },
    
    # Clean up orphaned images every week
    'cleanup-orphaned-images': {
        'task': 'app.tasks.images.cleanup_orphaned_images',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Weekly on Sunday at 3:00 AM
    },
    
    # Generate missing thumbnails every day at 4 AM
    'generate-missing-thumbnails': {
        'task': 'app.tasks.images.generate_image_thumbnails',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4:00 AM
    },
}

# Task time limits
task_soft_time_limit = 300  # 5 minutes
task_time_limit = 600       # 10 minutes

# Result backend settings
result_expires = 3600  # 1 hour

# Error handling
task_reject_on_worker_lost = True
task_ignore_result = False

# Monitoring
worker_send_task_events = True
task_send_sent_event = True
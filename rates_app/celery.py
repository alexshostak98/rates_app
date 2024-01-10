from celery import Celery

from rates_app import settings

app = Celery('rates_app', broker=settings.CELERY_BROKER_URL)


class Config:
    imports = ('rates_app.clients_module.tasks',)
    task_ignore_result = True


app.config_from_object(Config)

app.conf.beat_schedule = {
    'get-rates': {
        'task': 'rates_app.clients_module.tasks.get_rates_by_client',
        'schedule': 1.0,
    },
}

from django.core.management.base import BaseCommand
from audit.models import TaskLog

class Command(BaseCommand):
    help = 'Cron placeholder'

    def handle(self, *args, **options):
        task = TaskLog.objects.create(command=self.__module__.split('.')[-1])
        task.status = 'finished'
        task.save(update_fields=['status'])
        self.stdout.write('done')

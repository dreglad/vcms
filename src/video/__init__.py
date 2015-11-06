# -*- coding: utf-8 -*- #

def init_scheduler():
    from jobs import scheduled
    import django_rq
    from collections import defaultdict
    import datetime

    scheduler = django_rq.get_scheduler('default')

    jobs = scheduler.get_jobs()
    functions = defaultdict(lambda: list())

    map(lambda x: functions[x.func].append(x.meta.get('interval')), jobs)

    now = datetime.datetime.now()

    def schedule_once(func, interval):
        """
        Schedule job once or reschedule when interval changes
        """
        if not func in functions or not interval in functions[func]\
                or len(functions[func])>1:

            # clear all scheduled jobs for this function
            map(scheduler.cancel, filter(lambda x: x.func==func, jobs))

            # schedule with new interval
            scheduler.schedule(now+datetime.timedelta(seconds=interval), func,
                    interval=interval)

    schedule_once(scheduled.distribucion_job, interval=60*2)

init_scheduler()

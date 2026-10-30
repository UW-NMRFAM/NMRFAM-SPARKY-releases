import sched, time

class SparkyTimer(object):
    def __init__(self, interval, function, args):
        self.schedule = sched.scheduler(time.time, time.sleep)
        self.interval = interval
        self.is_running = False
        self.function = function
        self.args = args
        self.event = None

    def periodic(self, action, actionargs=()):
        if self.is_running:
            self.event = self.schedule.enter(self.interval, 1, self.periodic, (action, actionargs))
            action(*actionargs)

    def start(self):
        self.is_running = True
        self.periodic(self.function, self.args)
        self.schedule.run( )

    def stop(self):
        self.is_running = False
        if self.schedule and self.event:
            self.schedule.cancel(self.event)


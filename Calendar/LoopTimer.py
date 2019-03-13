from datetime import datetime, timedelta

class LoopTimer(object):
    """Manages loop times and sleeps until
    next loop."""
    def __init__(self, loop_interval, run_on_hour=False):
        self.interval = loop_interval
        self.on_hour = run_on_hour
        self.loop_history = []

    def begin_loop(self):
        begin_time = datetime.now()
        print('\n_________Starting new loop___________')
        print('Date: ' + begin_time.strftime('%a %d %b %y') + ', time: ' + begin_time.strftime('%H:%M') + '\n')
        self.__add_beginning__(begin_time)

    def __add_beginning__(self, time):
        self.loop_history.append((time,))

    def __add_ending__(self, time):
        current = self.get_current()
        self.loop_history[-1] = (current[0], time)

    def end_loop(self):
        end_time = datetime.now()
        self.__add_ending__(end_time)

    def get_current(self):
        return self.loop_history[-1]

    def time_until_next(self):
        interval_duration = timedelta(minutes=self.interval)
        loop_duration = self.get_last_duration()
        sleep_time = interval_duration - loop_duration
        if self.on_hour:
            time_until_hour = self.get_time_to_next_hour()
            if time_until_hour < sleep_time:
                return time_until_hour
        return sleep_time

    def get_last_duration(self):
        if len(self.loop_history) == 0:
            return
        begin, end = self.loop_history[-1]
        return end - begin

    def get_time_to_next_hour(self):
        cur = datetime.now()
        rounded = datetime(cur.year, cur.month, cur.day, cur.hour)
        next_hour_time = rounded + timedelta(hours=1)
        return  next_hour_time - datetime.now()

    def is_new_hour_loop(self):
        if len(self.loop_history) < 2:
            return False
        previous_loop = self.loop_history[-2]
        current_loop = self.get_current()

        if previous_loop[0].hour != current_loop[0].hour:
            return True
        else:
            return False
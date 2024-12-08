class Calendar:
    def __init__(self):
        self.days: list[Day] = []

    def create_day_event(self, day):
        self.days.append(day)

    def read_day_event(self, daytime):
        for day in self.days:
            if day.date == daytime:
                return day.read_events()

    def update_day_event(self, daytime, time, description):
        for day in self.days:
            if day.date == daytime:
                day.update_event(time, description)

    def delete_day_event(self, daytime, time):
        for day in self.days:
            if day.date == daytime:
                day.delete_event(time)


class Day:
    def __init__(self, date: str):
        self.date: str = date
        self.events: list[Event] = []

    def create_event(self, event):
        self.events.append(event)

    def read_events(self) -> list[str]:
        return [f"{ev.event_time}: {ev.description}" for ev in self.events]

    def update_event(self, time: str, description: str):
        for ev in self.events:
            if ev.event_time == time:
                ev.description = description

    def delete_event(self, time: str):
        for ev in self.events:
            if ev.event_time == time:
                self.events.remove(ev)


class Event:
    def __init__(self, time: str, description: str):
        self.event_time: str = time
        self.description: str = description
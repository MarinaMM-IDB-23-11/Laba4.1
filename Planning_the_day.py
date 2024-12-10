class Event: #событие
    def __init__(self, time: str, description: str):
        self.event_time: str = time
        self.description: str = description


class Day: #день
    def __init__(self, date: str):
        self.date: str = date
        self.events: list[Event] = []

    def create_event(self, event: Event) -> None:
        self.events.append(event)

    def read_events(self) -> list[str]:
        return [f"{ev.event_time}: {ev.description}" for ev in self.events]

    def update_event(self, time: str, description: str):
        for ev in self.events:
            if ev.event_time == time:
                ev.description = description

    def delete_event(self, time: str) -> None:
        for ev in self.events:
            if ev.event_time == time:
                self.events.remove(ev)


class Calendar: #хранилище дней
    def __init__(self):
        self.days: list[Day] = []

    def create_day_event(self, day: Day) -> None:
        self.days.append(day)

    def read_day_event(self, daytime: str) -> list[str]:
        for day in self.days:
            if day.date == daytime:
                return day.read_events()

    def update_day_event(self, daytime: str, time: str, description: str) -> None:
        for day in self.days:
            if day.date == daytime:
                day.update_event(time, description)

    def delete_day_event(self, daytime: str, time: str) -> None:
        for day in self.days:
            if day.date == daytime:
                day.delete_event(time)

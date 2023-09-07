from datetime import date

class Event:
    def __init__(self, name, start_date, end_date, target_funds, event_listener):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.target_funds = target_funds
        self.event_listener = event_listener
        self.total_raised = 0.0
        self.goal_achieved = False
        self.donations = []

    def add_donation(self, donation):
        pass

class Donation:
    def __init__(self, donor_name, amount, date):
        self.donor_name = donor_name
        self.amount = amount
        self.date = date

class EventListener:
    def update_total_raised(self, event, donation):
        pass

    def check_goal_achievement(self, event):
        pass

    def send_thank_you(self, donation):
        pass
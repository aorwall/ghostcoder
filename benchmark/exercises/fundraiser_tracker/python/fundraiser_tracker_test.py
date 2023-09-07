import unittest
from datetime import date
from fundraiser_tracker import Event, Donation, EventListener

class TestFundraiserTracker(unittest.TestCase):
    def setUp(self):
        self.event_listener = EventListener()
        self.event = Event('Charity Run', date(2022, 1, 1), date(2022, 1, 31), 10000.0, self.event_listener)
        self.donation1 = Donation('John Doe', 5000.0, date(2022, 1, 5))
        self.donation2 = Donation('Jane Doe', 6000.0, date(2022, 1, 10))

    def test_event_creation(self):
        self.assertEqual(self.event.name, 'Charity Run')
        self.assertEqual(self.event.start_date, date(2022, 1, 1))
        self.assertEqual(self.event.end_date, date(2022, 1, 31))
        self.assertEqual(self.event.target_funds, 10000.0)

    def test_donation_creation(self):
        self.assertEqual(self.donation1.donor_name, 'John Doe')
        self.assertEqual(self.donation1.amount, 5000.0)
        self.assertEqual(self.donation1.date, date(2022, 1, 5))

    def test_event_listener(self):
        self.event.add_donation(self.donation1)
        self.assertEqual(self.event.total_raised, 5000.0)
        self.event.add_donation(self.donation2)
        self.assertEqual(self.event.total_raised, 11000.0)
        self.assertTrue(self.event.goal_achieved)

if __name__ == '__main__':
    unittest.main()
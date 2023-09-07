# Non-profit Fundraiser Event Tracker

## Description
A large part of non-profit management involves organizing fundraisers and tracking the donations made during such events. Your task is to develop a system that can track the various aspects of a fundraising event and respond to changes in the funds being raised.

## Instructions
1. Create a class 'Event' that stores the details of a fundraising event. Key details include the event's name (String), start date (Date), end date (Date), and target funds to be raised (Double).
2. An event can have many 'Donations' made by various donors. Create a class 'Donation' that includes details like the donor's name (String), the donation amount (Double), and the donation date (Date).
3. Implement a method in the 'Event' class that is triggered whenever a donation is made. This method will update the total amount raised so far and compare it with the event's target funds.
4. To handle these updates, implement an 'Event Listener' class that checks if the total amount raised has met or exceeded the target for the fundraiser. If so, it triggers another method to announce the achievement of the fundraising goal.
5. Implement another method in the 'Event Listener' class that sends a 'Thank you' message to the donor every time a donation is updated.
6. All events along with their effects should be stored in a data structure (like a List or an Array) and retrieved in chronological order.

## Constraints
1. The implementation needs to be able to handle the creation of multiple unique 'Event' objects with different target funds.
2. 'Donation' objects can be created at different times, from different donors, and with variable amounts. The 'Event Listener' class must correctly react to each donation with the appropriate response.
3. Ensure all methods in the 'Event Listener' class are in sync and can handle rising amounts raised during a highly active fundraiser.
4. The system should appropriately handle failures and provide a mechanism for retrying failed operations where necessary.
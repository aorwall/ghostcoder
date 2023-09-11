import concurrent.futures
from typing import List

class Property:
    def __init__(self, location: str, square_footage: int, bedrooms: int, bathrooms: int, age: int, price: int = 0):
        self.location = location
        self.square_footage = square_footage
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.age = age
        self.price = price

def calculate_price(property: Property) -> Property:
    price = property.square_footage * 200 + property.bedrooms * 5000 - property.age * 1000
    return Property(property.location, property.square_footage, property.bedrooms, property.bathrooms, property.age, price)

def calculate_prices_concurrently(properties: List[Property]) -> List[Property]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        properties = list(executor.map(calculate_price, properties))
    return properties
def calculate_price(property: Property) -> None:
    base_price = property.square_footage * 200 + property.bedrooms * 5000 - property.age * 1000
    property.price = base_price
import concurrent.futures
from typing import List

class Property:
    def __init__(self, location: str, square_footage: int, bedrooms: int, bathrooms: int, age: int) -> None:
        self.location = location
        self.square_footage = square_footage
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.age = age
        self.price = None

def calculate_price(property: Property) -> float:
    base_price = property.square_footage * 200 + property.bedrooms * 5000 - property.age * 1000
    return base_price

def calculate_price(property: Property) -> Property:
    pass

def calculate_prices_concurrently(properties: List[Property]) -> List[Property]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(calculate_price, p) for p in properties]
        for future, prop in zip(futures, properties):
            future.result()
    return properties
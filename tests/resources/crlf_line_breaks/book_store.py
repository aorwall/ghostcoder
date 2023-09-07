from collections import Counter
def total(basket):
    # Count how many times each book appears in the basket and sort them by price from high to low.
    counts = sorted([(price, count)
                   for book, count in Counter(basket).items() if book in PRICES], reverse=True)

    # Initialize variables to keep track of the discounted prices and remaining books after applying group offers.
    total_discounted = 0
    remaining_books = []

    while counts:
        # Apply groups of five first, then three, then two until there are no more books left.
        price, count = counts[0]
        if count >= 5:
            total_discounted += 45 * 5
            counts[0] = (price, count % 5)
            counts = [(p, c + (count // 5)) for p, c in counts[1:] if p == price] + counts[:1]
        elif count >= 3:
            total_discounted += 45 * 3
            counts[0] = (price, count % 3)
            counts = [(p, c + (count // 3)) for p, c in counts[1:] if p == price] + counts[:1]
        elif count >= 2:
            total_discounted += 45 * 2
            counts[0] = (price, count % 2)
            counts = [(p, c + (count // 2)) for p, c in counts[1:] if p == price] + counts[:1]
        else:
            total_discounted += price * count
            remaining_books.extend([book] * count)
            del counts[0]

    # Calculate the final sum with any remaining books not included in group offers.
    return total_discounted + sum(PRICES[book] for book in remaining_books)

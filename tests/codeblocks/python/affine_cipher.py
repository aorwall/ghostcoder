def encode(plain_text, a, b):
    if not are_coprime(a, 26):
        raise ValueError("a and m must be coprime.")
    ciphered_text = ''
    for char in plain_text:
        if char.isalpha():
            i = ord(char.lower()) - 97
            ciphered_text += chr((a * i + b) % 26 + 97)
    return ' '.join(ciphered_text[i:i+5] for i in range(0, len(ciphered_text), 5))


def decode(ciphered_text, a, b):
    if not are_coprime(a, 26):
        raise ValueError("a and m must be coprime.")
    plain_text = ''
    for char in ciphered_text:
        if char.isalpha():
            y = ord(char) - 97
            plain_text += chr((mod_inverse(a, 26) * (y - b)) % 26 + 97)
    return plain_text


def are_coprime(a, b):
    while b != 0:
        a, b = b, a % b
    return a == 1


def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None
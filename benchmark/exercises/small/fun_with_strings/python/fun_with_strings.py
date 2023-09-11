# Define the phonetic alphabet
phonetic_alphabet = {
    'alpha': 'a',
    'bravo': 'b',
    'charlie': 'c',
    'delta': 'd',
    'echo': 'e',
    'foxtrot': 'f',
    'golf': 'g',
    'hotel': 'h',
    'india': 'i',
    'juliet': 'j',
    'kilo': 'k',
    'lima': 'l',
    'mike': 'm',
    'november': 'n',
    'oscar': 'o',
    'papa': 'p',
    'quebec': 'q',
    'romeo': 'r',
    'sierra': 's',
    'tango': 't',
    'uniform': 'u',
    'victor': 'v',
    'whiskey': 'w',
    'xray': 'x',
    'yankee': 'y',
    'zulu': 'z'
}

def decode_string(encoded_string):
    # Split the string into words
    words = encoded_string.split()
    # Reverse the list of words
    words.reverse()
    # Decode each word
    decoded_string = ''.join([phonetic_alphabet[word.lower()] if word.islower() else phonetic_alphabet[word.lower()].upper() for word in words])
    return decoded_string
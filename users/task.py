import re


def validate_egyptian_phone_number(phone_number):
    # Regular expression for Egyptian phone numbers
    pattern = re.compile(r' ^ (\+201 | 01 | 00201)[0 - 2, 5]{1}[0 - 9]{8}')

    # Match the phone number against the pattern
    match = pattern.match(phone_number)

    # Return True if the phone number is valid, False otherwise
    return bool(match)
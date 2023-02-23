import string, random

numbers = ["0","1","2","3","4","5","6","7","8","9"]
alphabet = list(string.ascii_uppercase)

def generate_code():
    code = ""
    for i in range(6):
        if random.choice("10") == "1":
            code += random.choice(numbers)
        else:
            code += random.choice(alphabet)

    return code

print(generate_code())
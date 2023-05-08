import random

maxcount = 10
count = maxcount

while count != 0:
    a = random.randint(1, 5)
    b = random.randint(1, 5)
    
    res = input(f"{a} x {b} = ")
    if (int(res) != int(a*b)):
        print(f"NAN! C'était {a*b}")
        count = maxcount
    else:
        print("Bien")
        count = count - 1
    print(f"Encore {count} multiplications à trouver")

print("BRAVO \o/")

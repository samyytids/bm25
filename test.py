import os

# features = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
features = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
index = 0

while True:
    jump = input("Gimme a jump: ")
    if "." in jump:
        print(". check")
        jump = float(jump)
        print("floated")
        print(jump)
        for idx, f in enumerate(features):
            if f <= jump:
                break
        print("New idx")
        jump = idx - index
        print("Updated jump value")
    else:
        print("Went with the else?")
        jump = int(jump)
    print("Jump: ", jump)
    index += jump
    print(features[index])
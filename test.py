# Initialize the  variables
min, max = 0, 0
# Loop to read 5 numbers from the user
for i in range(1, 6):
    number = float(input(f"Enter number {i}:   "))  # Read a number
    if i == 1:
        min = number
        max = number
    else:
        if number < min:
            min = number
        if number > max:
            max = number
# Display the min and max after the loop ends
print(f"\nThe minimum of the numbers is: {min}")
print(f"\nThe maximum of the numbers is: {max}")




i = 20
while i > 0:
    print(i)
    i -= 5  

n = 0
while n < 5:
    print(f'Inside the loop, the value of n is {n}.')
    n = n + 1



# The target variable here is 'num'
for num in range(1, 6):
    square = num ** 2  # Using 'num' to calculate its square
    print(f"The square of {num} is {square}")

for num in range(10, 0, -2):
    print(num, end=", ")

# MISTAKE


# MISTAKE
while True:
    count = 0  # This resets to 0 every single time the loop restarts
    count += 1
    if count > 10:
        break

# MISTAKE
i = 0
while i < 5:
    print(i)
i += 1  # This is outside the loop! The loop only sees print(i)




# This for loop iterates over the list [1, 2, 3, 4, 5]
for num in ["Hello", 100, "World!", 0, 1, True]:
    print(num)


for ch in "hello":
    print(ch)

fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

items = ["a", "b", "c"]
for idx, val in enumerate(items):
    print(idx, val)

names = ["Ada", "Linus", "Grace"]
ages = [36, 55, 44]
for name, age in zip(names, ages):
    print(name, age)
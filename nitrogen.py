import request
import random
import string
import time

print("""nitro Gen 1.0""")
time.sleep(2)
print("NITRO.CODES.txt/valid")
time.sleep(0.3)
print(" Nitro Gen Checker")
time.sleep(0.2)

num = int(input('Input How Many Codes to Generate and Check: '))

valid_codes = []

print("Your nitro codes are being generated and checked, be patient if you entered a high number!")

start = time.time()

for i in range(num):
    code = "".join(random.choices(
        string.ascii_uppercase + string.digits + string.ascii_lowercase,
        k = 16
    ))

    nitro_url = f"https://discord.gift/{code}"
    url = "https://discordapp.com/api/v6/entitlements/gift-codes/" + code + "?with_application=false&with_subscription_plan=true"

    r = requests.get(url)

    if r.status_code == 200:
        print(f" YES  | {nitro_url} ")
        valid_codes.append(nitro_url)
    else:
        print(f" NO | {nitro_url} ")

print(f"\nGenerated and checked {num} codes | Time taken: {time.time() - start}")

if valid_codes:
    with open("Valid Codes.txt", "w", encoding='utf-8') as valid_file:
        for valid_code in valid_codes:
            valid_file.write(f"{valid_code}\n")
    print(f"Found {len(valid_codes)} valid codes. They have been saved to Valid Codes.txt")
else:
    print("No valid codes found this time.")

input("\nYou have generated and checked codes. Now press enter to close this.")

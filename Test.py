import requests
import time
import threading
import random
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# List of available colors from colorama
colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE]

def fetch_pet_info(headers, account_number, color):
    try:
        pet_response = requests.get("https://api-clicker.pixelverse.xyz/api/pets", headers=headers)
        if pet_response.status_code == 200:
            pet_data = pet_response.json()
            pets = pet_data.get('data', [])
            print(color + Style.BRIGHT + f"Pet Information for account {account_number}:")
            for pet in pets:
                name = pet.get('name')
                user_pet = pet.get('userPet', {})
                level = user_pet.get('level')
                stats = user_pet.get('stats', [])

                # Initialize default values
                max_energy = power = recharge_speed = None

                # Extract specific stats
                for stat in stats:
                    stat_name = stat.get('petsStat', {}).get('name')
                    current_value = stat.get('currentValue')
                    if stat_name == 'Max energy':
                        max_energy = current_value
                    elif stat_name == 'Damage':
                        power = current_value
                    elif stat_name == 'Energy restoration':
                        recharge_speed = current_value

                print(color + Style.BRIGHT + f"Name: {name}, Level: {level}, Max energy: {max_energy}, Power: {power}, Recharge speed: {recharge_speed}")
            return pets  # Return the pet data for further processing
        else:
            print(color + Style.BRIGHT + f"Failed to fetch pet information for account {account_number}. Status code:", pet_response.status_code)
    except Exception as e:
        print(color + Style.BRIGHT + f"Error fetching pet information for account {account_number}:", e)
    return []

def upgrade_pet(headers, pet, account_number, color):
    try:
        user_pet = pet.get('userPet', {})
        pet_id = user_pet.get('id')

        upgrade_response = requests.post(f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{pet_id}/level-up", headers=headers)
        if upgrade_response.status_code == 201:
            print(color + Style.BRIGHT + f"Pet with ID {pet_id} upgraded successfully for account {account_number}.")
            # Fetch and display the updated pet information
            fetch_pet_info(headers, account_number, color)
        else:
            print(color + Style.BRIGHT + f"Failed to upgrade pet with ID {pet_id} for account {account_number}. Status code:", upgrade_response.status_code)
    except Exception as e:
        print(color + Style.BRIGHT + f"Error upgrading pet with ID {pet_id} for account {account_number}:", e)

def mainLoop(headers, auto_upgrade, account_number, color):
    claim_count = 0
    claimed_amount_offset = account_number  # Initialize offset based on account number
    try:
        # Login and get user information
        user_response = requests.get("https://api-clicker.pixelverse.xyz/api/users", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            telegram_user = user_data.get("telegramUserId")
            claim_count = user_data.get("clicksCount", 0)
            if telegram_user:
                print(color + Style.BRIGHT + f"Login successful for account {account_number}!")
            else:
                print(color + Style.BRIGHT + f"Login successful for account {account_number}! But Telegram User ID not found.")
        else:
            print(color + Style.BRIGHT + f"Login failed for account {account_number}. Status code:", user_response.status_code)
            return

        # Fetch and display pet information after login
        pets = fetch_pet_info(headers, account_number, color)
        num_claims = 0

        # Add delay before starting claims
        for remaining in range(5, 0, -1):
            print(f"Wait {remaining} seconds to start the claim", end="\r")
            time.sleep(1)

        while True:
            for remaining in range(300, 0, -1):  # 5 minutes delay
                print(f"Next claim in {remaining} seconds for all accounts", end="\r")
                time.sleep(1)

            claim_response = requests.post("https://api-clicker.pixelverse.xyz/api/mining/claim", headers=headers)
            if claim_response.status_code == 201:
                claim_data = claim_response.json()
                claimed_amount = claim_data.get("claimedAmount", 0) + claimed_amount_offset
                claim_count += claimed_amount
                num_claims += 1
                print(color + Style.BRIGHT + f"Claimed Amount for account {account_number}: " + str(claimed_amount) + " ,Total Earned: " + str(claim_count))
                
                if auto_upgrade and num_claims % 10 == 0:
                    print(color + Style.BRIGHT + f"Auto-upgrading pets for account {account_number}...")
                    for pet in pets:
                        upgrade_pet(headers, pet, account_number, color)
                    
                    # Re-fetch pet information after upgrades
                    pets = fetch_pet_info(headers, account_number, color)
            else:
                print(color + Style.BRIGHT + f"Claim failed for account {account_number}")

    except Exception as e:
        print(color + Style.BRIGHT + f"Error in account {account_number}:", e)

# Read initdata from file
initdata_list = []
try:
    with open("data.txt", "r") as file:
        for line in file:
            initdata = line.strip()
            if initdata:
                initdata_list.append(initdata)
    if initdata_list:
        print(Fore.GREEN + Style.BRIGHT + "Berhasil mengambil data")
    else:
        print(Fore.RED + Style.BRIGHT + "Gagal mengambil data: File kosong")
        exit(1)
except FileNotFoundError:
    print(Fore.RED + Style.BRIGHT + "Gagal mengambil data: File tidak ditemukan")
    exit(1)
except Exception as e:
    print(Fore.RED + Style.BRIGHT + f"Gagal mengambil data: {e}")
    exit(1)

# Headers template
header = {
    'Accept': 'application/json, text/plain, */*',
    'Cache-Control': 'no-cache',
    'Origin': 'https://sexyzbot.pxlvrs.io',
    'Pragma': 'no-cache',
    'Referer': 'https://sexyzbot.pxlvrs.io/',
    'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

# Ask the user if they want to enable auto-upgrade
auto_upgrade_choice = input("Enable auto-upgrade for pets? (y/n): ").strip().lower()
auto_upgrade = auto_upgrade_choice == 'y'

# Function to run mainLoop in a thread
def run_threaded(headers, auto_upgrade, account_number, color):
    thread = threading.Thread(target=mainLoop, args=(headers, auto_upgrade, account_number, color))
    thread.start()
    return thread

# Start threads for all accounts
threads = []
for account_number, initdata in enumerate(initdata_list, start=1):
    headers = header.copy()
    headers['Initdata'] = initdata
    color = random.choice(colors)  # Choose a random color for each account
    threads.append(run_threaded(headers, auto_upgrade, account_number, color))

# Wait for all threads to finish
for thread in threads:
    thread.join()

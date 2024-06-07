import requests
import time

def fetch_pet_info(headers):
    try:
        pet_response = requests.get("https://api-clicker.pixelverse.xyz/api/pets", headers=headers)
        if pet_response.status_code == 200:
            pet_data = pet_response.json()
            pets = pet_data.get('data', [])
            print("Pet Information:")
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

                print(f"Name: {name}, Level: {level}, Max energy: {max_energy}, Power: {power}, Recharge speed: {recharge_speed}")
            return pets  # Return the pet data for further processing
        else:
            print("Failed to fetch pet information. Status code:", pet_response.status_code)
    except Exception as e:
        print("Error fetching pet information:", e)
    return []

def upgrade_pet(headers, pet):
    try:
        user_pet = pet.get('userPet', {})
        pet_id = user_pet.get('id')

        upgrade_response = requests.post(f"https://api-clicker.pixelverse.xyz/api/pets/user-pets/{pet_id}/level-up", headers=headers)
        if upgrade_response.status_code == 201:
            print(f"Pet with ID {pet_id} upgraded successfully.")
            # Fetch and display the updated pet information
            fetch_pet_info(headers)
        else:
            print(f"Failed to upgrade pet with ID {pet_id}. Status code:", upgrade_response.status_code)
    except Exception as e:
        print(f"Error upgrading pet with ID {pet_id}:", e)

def mainLoop(headers, auto_upgrade):
    claim_count = 0
    try:
        # Login and get user information
        user_response = requests.get("https://api-clicker.pixelverse.xyz/api/users", headers=headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            telegram_user = user_data.get("telegramUserId")
            claim_count = user_data.get("clicksCount", 0)
            if telegram_user:
                print("Login successful!")
            else:
                print("Login successful! But Telegram User ID not found.")
        else:
            print("Login failed. Status code:", user_response.status_code)
            return

        # Fetch and display pet information after login
        pets = fetch_pet_info(headers)
        num_claims = 0

        while True:
            for remaining in range(300, 0, -1):  # 5 minutes delay
                print(f"Next claim in {remaining} seconds", end="\r")
                time.sleep(1)
                
            claim_response = requests.post("https://api-clicker.pixelverse.xyz/api/mining/claim", headers=headers)
            if claim_response.status_code == 201:
                claim_data = claim_response.json()
                claimed_amount = claim_data.get("claimedAmount", 0)
                claim_count += claimed_amount
                num_claims += 1
                print("Claimed Amount: " + str(claimed_amount) + " ,Total Earned: " + str(claim_count))
                
                if auto_upgrade and num_claims % 10 == 0:
                    print("Auto-upgrading pets...")
                    for pet in pets:
                        upgrade_pet(headers, pet)
                    
                    # Re-fetch pet information after upgrades
                    pets = fetch_pet_info(headers)
            else:
                print("Claim failed")

    except Exception as e:
        print("Error:", e)

# Input
initdata = input("Initdata: ")

# Headers
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Cache-Control': 'no-cache',
    'Initdata': initdata,
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

mainLoop(headers, auto_upgrade)

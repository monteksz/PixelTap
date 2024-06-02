import requests
import time

def mainLoop(headers):
    claim_count = 0
    try:
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

        while True:
            for remaining in range(25, 0, -1):
                print(f"Next claim in {remaining} seconds", end="\r")
                time.sleep(1)
                
            claim_response = requests.post("https://api-clicker.pixelverse.xyz/api/mining/claim", headers=headers)
            if claim_response.status_code == 201:
                claim_data = claim_response.json()
                claimed_amount = claim_data.get("claimedAmount", 0)
                claim_count += claimed_amount
                print("Claimed Amount: " + str(claimed_amount) + " ,Total Earned: " + str(claim_count))
            elif claim_response.status_code == 409:
                print("Claim already")
            else:
                print("Claim failed")

    except Exception as e:
        print("Error:", e)

# Input
initdata = input("Initdata: ")
tg_id = input("Tg-Id: ")

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
    'Tg-Id': tg_id,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

mainLoop(headers)
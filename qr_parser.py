import re
import csv
import requests
import json
from termcolor import colored

API_KEY_FILE = 'api_key.json'
MOUSER_API_URL = "https://api.mouser.com/api/v1/search/partnumber"
OUTPUT_FILENAME = "output.csv"

def load_api_key(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)['api_key']

def fetch_mouser(part_number, api_key):
    headers = {"Content-Type": "application/json"}
    payload = {
        "SearchByPartRequest": {
            "mouserPartNumber": part_number
        }
    }
    try:
        response = requests.post(MOUSER_API_URL, json=payload, headers=headers, params={"apiKey": api_key}, timeout=5)
        response.raise_for_status()
        data = response.json()
        parts = data.get("SearchResults", {}).get("Parts", [])
        if parts:
            part_info = parts[0]
            return {
                "manufacturer": part_info.get("Manufacturer"),
                "description": part_info.get("Description", "Description not available")
            }
    except requests.RequestException as e:
        print(colored(f"Error fetching data from Mouser API: {e}", 'red'))
    return {"manufacturer": "Unknown", "description": "Description not found"}

def parse_qr_code(data):
    patterns = [
        re.compile(r'QTY:(\d+) PN:([\w-]+) PO:([\w/]+) CPO:([\w-]+) MFR:([\w-]+) MPN:([\w-]+)'),  # TME
        re.compile(r'\{[^}]*pbn:[^,]*,on:[^,]*,pc:[^,]*,pm:([^,]*),qty:(\d+),[^}]*\}')  # LCSC
    ]
    components = []
    for line in data.splitlines():
        line = line.strip()
        for pattern in patterns:
            match = pattern.match(line)
            if match:
                if len(match.groups()) == 6:  # First format
                    components.append({
                        "manufacturer": match.group(5),
                        "part_number": match.group(2),
                        "quantity": int(match.group(1)),
                    })
                elif len(match.groups()) == 2:  # Second format
                    components.append({
                        "manufacturer": "Unknown",
                        "part_number": match.group(1),
                        "quantity": int(match.group(2)),
                    })
    return components

def display_component(component, data):
    print(colored(f"Manufacturer: {data['manufacturer']}", 'cyan'))
    print(colored(f"Part Number: {component['part_number']}", 'green'))
    print(colored(f"Quantity: {component['quantity']}", 'yellow'))
    print(colored(f"Description: {data['description']}\n", 'magenta'))

def save_to_csv(components, filename, api_key):
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for component in components:
            data = fetch_mouser(component["part_number"], api_key)
            writer.writerow([
                data["manufacturer"],
                component["part_number"],
                component["quantity"],
                data["description"]
            ])
    print(colored(f"Data saved to {filename}\n", 'green'))

def main():
    api_key = load_api_key(API_KEY_FILE)
    while True:
        data = input(colored("Enter the QR code data (or type 'exit' to quit): ", 'blue')).strip()
        if data.lower() == 'exit':
            print(colored("Exiting the program. Goodbye!", 'red'))
            break
        components = parse_qr_code(data)
        if components:
            for component in components:
                data = fetch_mouser(component["part_number"], api_key)
                display_component(component, data)
            save = input(colored("Do you want to save these components to a CSV file? (yes/no): ", 'blue')).strip().lower()
            if save in ["yes", "y"]:
                save_to_csv(components, OUTPUT_FILENAME, api_key)
            else:
                print(colored("Data not saved.\n", 'red'))
        else:
            print(colored("No valid components found in the input.\n", 'red'))

if __name__ == "__main__":
    main()

import re
import csv
import requests
import json
from termcolor import colored


def fetch_mouser(part_number):
    """
    Fetches a description for the given part number using the Mouser API.
    Replace 'YOUR_MOUSER_API_KEY' with your valid API key.
    """
    api_key = "YOUR_MOUSER_API_KEY"
    #open the file and read the api key
    with open('api_key.json', 'r') as file:
        apk = json.load(file)

    api_key = apk['api_key']
    search_url = "https://api.mouser.com/api/v1/search/partnumber"

    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "SearchByPartRequest": {
                "mouserPartNumber": part_number
            }
        }
        response = requests.post(search_url, json=payload, headers=headers, params={"apiKey": api_key}, timeout=5)
        response.raise_for_status()
        data = response.json()
        search_results = data.get("SearchResults")
        if search_results:
            parts = search_results.get("Parts")
            if parts:
                part_info = parts[0]
                manufacturer = part_info.get("Manufacturer")
                description = part_info.get("Description", "Description not available")
                return {"manufacturer": manufacturer, "descriprion": description}


    except requests.RequestException as e:
        print(colored(f"Error fetching data from Mouser API: {e}", 'red'))

    return "Description not found"




def parse_qr_code(data):
    # Define regex patterns for both formats
    patterns = [
        re.compile(r'QTY:(\d+) PN:([\w-]+) PO:([\w/]+) CPO:([\w-]+) MFR:([\w-]+) MPN:([\w-]+)'), #TME
        re.compile(r'\{[^}]*pbn:[^,]*,on:[^,]*,pc:[^,]*,pm:([^,]*),qty:(\d+),[^}]*\}') #LCSC
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

def display_and_save(components, filename="output.csv"):
    for component in components:
        data = fetch_mouser(component["part_number"])
        print(colored(f"Manufacturer: {data['manufacturer']}", 'cyan'))
        print(colored(f"Part Number: {component['part_number']}", 'green'))
        print(colored(f"Quantity: {component['quantity']}", 'yellow'))
        print(colored(f"Description: {data['descriprion']}\n", 'magenta'))

    save = input(colored("Do you want to save these components to a CSV file? (yes/no): ", 'blue')).strip().lower()
    if save in ["yes", "y"]:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for component in components:
                data = fetch_mouser(component["part_number"])
                if component["manufacturer"] and component["part_number"] and component["quantity"]:
                    writer.writerow([
                        data["manufacturer"],
                        component["part_number"],
                        component["quantity"],
                        data["descriprion"]
                    ])
        print(colored(f"Data saved to {filename}\n", 'green'))
    else:
        print(colored("Data not saved.\n", 'red'))

def main():
    while True:
        data = input(colored("Enter the QR code data (or type 'exit' to quit): ", 'blue')).strip()
        if data.lower() == 'exit':
            print(colored("Exiting the program. Goodbye!", 'red'))
            break
        components = parse_qr_code(data)
        if components:
            display_and_save(components)
        else:
            print(colored("No valid components found in the input.\n", 'red'))

if __name__ == "__main__":
    main()


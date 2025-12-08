import json
import os
import pyperclip
import pyautogui
import time

PASSWORD_FILE = "passwords.json"
    
def load_passwords():
    if not os.path.exists(PASSWORD_FILE):
        return {}
    with open(PASSWORD_FILE, "r",encoding="utf-8") as file:
        return json.load(file)

def save_passwords(passwords):
    with open(PASSWORD_FILE, "w",encoding="utf-8") as file:
        json.dump(passwords, file, indent=4)

def add_password():
    service = input("Enter service name: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    passwords = load_passwords()
    passwords[service] = {"username": username, "password": password}
    save_passwords(passwords)
    print(f"Password for {service} saved.")

def delete_password():
    service = input("Enter service name: ")
    passwords = load_passwords()
    if service in passwords:
        confirm = input(f"Are you sure you want to delete '{service}'? (y/n): ").lower()
        if confirm == 'y':
            del passwords[service]
            save_passwords(passwords)
            print(f"Password for '{service}' deleted.")
        else:
            print("Deletion canceled.")
    else:
        print(f"No password found for '{service}'.")
        
def get_password_auto():
    service = input("Enter service name: ")
    passwords = load_passwords()
    if service in passwords:
        entry = passwords[service]
        print("Five seconds to focus to app/web and click username field")
        for i in range(5):
            print(f'\rWaiting {i + 1}/5 seconds', end='')
            time.sleep(1)
        #pyautogui.write(entry["username"])
        #pyautogui.press("tab")
        #pyautogui.write(entry["password"])
        #pyautogui.press("enter")
        pyperclip.copy(entry["username"])
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("tab")
        pyperclip.copy(entry["password"])
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")
    else:
        print("Service not found.")
        
def get_password():
    service = input("Enter service name: ")
    passwords = load_passwords()
    if service in passwords:
        entry = passwords[service]
        pyperclip.copy(entry["password"])
        print(f"Username: {entry['username']}")
        print("Password has been copied to clipboard.")
    else:
        print("Service not found.")

def list_services():
    passwords = load_passwords()
    if not passwords:
        print("No saved services.")
    else:
        print("Saved services:")
        for service in passwords:
            print(f"- {service}")
           
def exit_program():
    print("👋 Exiting. Stay safe!")
    exit()

def main():
    main_menu = {
    "1": {"label": "Add password", "action":add_password},
    "2": {"label": "Copy password", "action": get_password},
    "3": {"label": "Auto password set", "action": get_password_auto},
    "4": {"label": "List services", "action":list_services},
    "5": {"label": "Delete password", "action":delete_password},
    "6": {"label": "Exit", "action": exit_program}
    }
    while True:
        print("\nPassword Manager")
        
        for key,item in main_menu.items():
            print(f"{key}. {item['label']}")
            
        choice = input("Choose an option: ").strip()
        selected = main_menu.get(choice)
        
        if selected:
            selected['action']()
        else:
            print(f"{choice} is an invalid option.")

if __name__ == "__main__":
    main()

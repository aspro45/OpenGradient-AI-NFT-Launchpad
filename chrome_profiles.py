import os
import subprocess
import sys

# Default Chrome paths on Windows
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
]

def get_chrome_path():
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    return None

def launch_profile(profile_num):
    chrome_path = get_chrome_path()
    if not chrome_path:
        print("Error: Could not find Google Chrome installed on this system.")
        return

    # Create a directory setup for profiles in the current folder
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Chrome_Profiles")
    profile_dir = os.path.join(base_dir, f"Profile_{profile_num}")
    
    print(f"Launching Chrome Profile {profile_num}...")
    
    # Launch Chrome with the specific user data directory
    subprocess.Popen([
        chrome_path,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--new-window"
    ])

def main():
    print("===============================")
    print("=== Chrome Profile Launcher ===")
    print("===============================")
    print("This script helps you manage 10 isolated Chrome profiles.")
    print("Each profile will have its own separate cookies, extensions, and logins.")
    print("The profiles will be saved in a new 'Chrome_Profiles' folder here.")
    print("-" * 31)
    
    while True:
        try:
            print()
            choice = input(f"Enter profile number to launch (1-10) or 'all' to launch all [q to quit]: ").strip().lower()
            
            if choice == 'q':
                print("Exiting...")
                break
            elif choice == 'all':
                print("Launching all 10 profiles... (Warning: this might use a lot of RAM!)")
                for i in range(1, 11):
                    launch_profile(i)
            else:
                num = int(choice)
                if 1 <= num <= 10:
                    launch_profile(num)
                else:
                    print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Invalid input. Please enter a number from 1 to 10, 'all', or 'q'.")

if __name__ == "__main__":
    main()

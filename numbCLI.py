"""
-------------------------------------------------------------
Model Numbering Command-Line Interface (CLI) - numbCLI.py
-------------------------------------------------------------

Description:
    Provides an interactive CLI for users to interact with 
    the Model Numbering Service. Allows operations such 
    as adding model types, pulling numbers, confirming,
    releasing, and searching for model numbers.

Author:
    John DeHart (jdehart@avian.com)

Date:
    Created on: August 10, 2023 

License:
    MIT License

"""


import argparse
import requests
import cmd
import configparser
import os
import sys

# Clear the screen 
CLEAR_CMD = 'clear' if os.name == 'posix' else 'cls'

# Clear the console
def clear_console():
    os.system(CLEAR_CMD)

# Configuration utility functions
CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".model_cli_config")

def set_config(key, value):
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config_file.write(f"{key}={value}\n")

def get_config(key):
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            for line in config_file:
                k, v = line.strip().split('=')
                if k == key:
                    return v
    return None

# Read from the config file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = 'localhost'
PORT = config.get('DEFAULT', 'PORT', fallback='5001')
BASE_URL = get_config("BASE_URL") or f"http://{HOST}:{PORT}"

class NumberingCLI(cmd.Cmd):
    use_rawinput = True
    intro = "Welcome to the model numbering CLI. Type the number of the desired command from the list below:\n"
    prompt = "Select option: "

    menu = {
        "A": {"info": "Add - Model Type", "func": "add_model_type_prompt"},
        "L": {"info": "List - Model Types", "func": "list_model_types"},
        "P": {"info": "Pull - Model Number", "func": "pull_prompt"},
        "C": {"info": "Confirm - Model Number", "func": "confirm_prompt"},
        "R": {"info": "Release - Model Number", "func": "release_prompt"},
        "S": {"info": "Search - Model Number", "func": "search_prompt"},
        "E": {"info": "Edit - Model Number", "func": "edit_model_details_prompt"},
        "U": {"info": "Update - Base URL", "func": "set_base_url_prompt"},
        "X": {"info": "Exit", "func": "do_exit"},
    }

    def preloop(self):
        self.print_menu()

    def emptyline(self):
        self.print_menu()

    def print_menu(self):
        for key, entry in self.menu.items():
            print(f"{key}. {entry['info']}")

    def default(self, line):
        if line in self.menu:
            func_name = self.menu[line]['func']
            getattr(self, func_name)('')
        else:
            print("Invalid option. Please choose a valid number.")
            self.print_menu()

    def add_model_type_prompt(self, _):
        clear_console() # Clear console and list commands
        model_type = input("Enter model type (e.g. SYS): ")
        description = input("Enter description: ")
        self.do_add_model_type(f"{model_type} {description}")
        # Clear console and list commands
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def pull_prompt(self, _):
        clear_console() # Clear console and list commands
        model_type = input("Enter model type for which to retrieve a number (e.g. SYS): ")
        self.do_pull(model_type)
        # Clear console and list commands
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def list_model_types(self, _):
        clear_console() # Clear console and list commands
        print("Current Model Types:")  # Prints 50 dashes
        model_type = "List current model types: "
        print("-" * 50)  # Prints 50 dashes
        self.do_list_model_types(model_type)
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def confirm_prompt(self, _):
        clear_console() # Clear console and list commands
        model_number = input("Enter model number to confirm (e.g. SYS-0001): ")
        self.do_confirm(model_number)
        # Clear console and list commands
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def release_prompt(self, _):
        clear_console() # Clear console and list commands
        model_number = input("Enter model number to release (e.g. SYS-0001): ")
        self.do_release(model_number)
        # Clear console and list commands
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def search_prompt(self, _):
        clear_console() # Clear console and list commands
        model_number = input("Enter model number to search (e.g. SYS-0001): ")
        self.do_search(model_number)
        # Clear console and list commands
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def edit_model_details_prompt(self, _):
        clear_console() # Clear console and list commands
        model_number = input("Enter model number (e.g. SYS-0001): ")
        model_name = input('Enter model name (in quotes if there are spaces): ')
        model_notes = input('Enter model notes (in quotes if there are spaces): ')
        self.do_edit_model_details(f"{model_number} {model_name} {model_notes}")
        # Clear console and list commands
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def set_base_url_prompt(self, _):
        clear_console() # Clear console and list commands
        url = input("Enter the new base URL: ")
        self.do_set_base_url(url)
        # Clear console and list commands
        print("-" * 50)  # Prints 50 dashes
        self.print_menu()

    def do_add_model_type(self, args):
        """Add a new model type with a description. Usage: add_model_type <model_type> <description>"""
        args = args.split(maxsplit=1)
        if len(args) != 2:
            print("Usage: add_model_type <model_type> <description>")
            return

        model_type, description = args
        response = requests.post(f"{BASE_URL}/add_model_type/{model_type}/{description}")
        print(response.json().get("status", "An error occurred."))


    def do_list_model_types(self, _):
        """List available model types with their descriptions."""
        response = requests.get(f"{BASE_URL}/list_model_types")
        model_types = response.json().get("model_types", [])
        for model in model_types:
            print(f"Type: {model['type']}, Description: {model['description']}")


    def do_pull(self, model_type):
        """Retrieve and reserve the next available number for a given model type."""
        response = requests.get(f"{BASE_URL}/pull/{model_type}")
        try:
            number = response.json()["number"]
            formatted_number = f"{model_type}-{number:04}"
            print(formatted_number)
        except:
            print("Error:", response.json().get("error", "An error occurred."))

    def do_confirm(self, arg):
        """Confirm the use of a specific number for a given model type."""
        try:
            parser = argparse.ArgumentParser(prog="confirm", description="Confirm the use of a specific number for a given model type.")
            parser.add_argument("model_number", help="Model number in the format MODEL-NUMBER", type=str)
            args = parser.parse_args(arg.split())

            # Splitting the input and checking if it has the correct number of parts
            parts = args.model_number.split('-')
            if len(parts) != 2:
                raise ValueError("Invalid input format.")

            model_type, number = parts
            response = requests.post(f"{BASE_URL}/confirm/{model_type}/{number}")
            if response.status_code == 200:
                status = response.json()["status"]
                print(f"{status}: {model_type}-{number}")
            else:
                print(response.json()["error"])
            
        except (ValueError, argparse.ArgumentError):
            print("Invalid input format. Please use the format MODEL-NUMBER, e.g., SYS-0001")

    def do_release(self, arg):
        """Release a specific number for a given model type."""
        try:
            parser = argparse.ArgumentParser(prog="release", description="Release a specific number for a given model type.")
            parser.add_argument("model_number", help="Model number in the format MODEL-NUMBER", type=str)
            args = parser.parse_args(arg.split())

            # Splitting the input and checking if it has the correct number of parts
            parts = args.model_number.split('-')
            if len(parts) != 2:
                raise ValueError("Invalid input format.")

            model_type, number = parts
            response = requests.post(f"{BASE_URL}/release/{model_type}/{number}")
            if response.status_code == 200:
                print(response.json()["status"])
            else:
                print(response.json()["error"])
            
        except (ValueError, argparse.ArgumentError):
            print("Invalid input format. Please use the format MODEL-NUMBER, e.g., SYS-0001")

    def do_search(self, arg):
        """Search for a specific number for a given model type."""
        try:
            parser = argparse.ArgumentParser(prog="search", description="Search for a specific number for a given model type.")
            parser.add_argument("model_number", help="Model number in the format MODEL-NUMBER", type=str)
            args = parser.parse_args(arg.split())

            parts = args.model_number.split('-')
            if len(parts) != 2:
                raise ValueError("Invalid input format.")
            
            model_type, number = parts
            response = requests.get(f"{BASE_URL}/search/{model_type}/{number}")
            if response.status_code == 200:
                data = response.json()
                status = data["status"]
                model_name = data.get("model_name", "N/A")  # Default to "N/A" if not provided
                model_notes = data.get("model_notes", "N/A")  # Default to "N/A" if not provided
                
                # Checking the status to print the correct message
                if status == "pulled":
                    print(f"Model {model_type}-{number}: {status}, awaiting confirmation")
                elif status == "confirmed":
                    print(f"Model {model_type}-{number}: {status}")
                else:
                    print(f"Model {model_type}-{number}: {status}")

                # Display the model name and notes
                print(f"Model Name: {model_name}")
                print(f"Model Notes: {model_notes}")
                
            else:
                print(response.json()["error"])
            
        except (ValueError, argparse.ArgumentError):
            print("Invalid input format. Please use the format MODEL-NUMBER, e.g., SYS-0001")

    def do_edit_model_details(self, args):
        """Edit details for a specific model number. Usage: edit_model_details <model_number> "<model_name>" "<model_notes>" """
        try:
            # Split the arguments based on space first to separate model_number
            parts = args.split(maxsplit=1)
            model_number = parts[0]

            # Now, let's find model_name and model_notes enclosed in double quotes
            import shlex
            model_name, model_notes = shlex.split(parts[1])

            # Make the request to edit the model details
            payload = {
                "model_name": model_name,
                "model_notes": model_notes
            }
            response = requests.post(f"{BASE_URL}/edit_model_details/{model_number}", json=payload)

            # Print the server response or an error message
            print(response.json().get("status", "An error occurred."))

        except Exception as e:
            print(f"Error processing the command: {e}. Ensure the correct format is used.")

    def do_set_base_url(self, url):
        """Set the base URL for the CLI."""
        try:
            set_config("BASE_URL", url)
            global BASE_URL
            BASE_URL = url
            print(f"Base URL set to {url}")
        except Exception as e:
            print(f"Error setting base URL: {e}")

    def do_exit(self, _):
        """Exit the CLI."""
        print("Exiting the CLI...")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Numbering CLI")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    args = parser.parse_args()
    
    if args.non_interactive:
        print("Running in non-interactive mode. Use without --non-interactive to enter interactive mode.")
    else:
        NumberingCLI().cmdloop()

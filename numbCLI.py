import argparse
import requests
import cmd
import configparser
import os

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
    intro = "Welcome to the model numbering CLI. Type help or ? to list commands.\n"
    prompt = "(numbering) "

    def do_add_model_type(self, model_type):
        """Add a new model type."""
        response = requests.post(f"{BASE_URL}/add_model_type/{model_type}")
        print(response.json().get("status", "An error occurred."))

    def do_list_model_types(self, _):
        """List available model types."""
        response = requests.get(f"{BASE_URL}/list_model_types")
        model_types = response.json().get("model_types", [])
        for model in model_types:
            print(model)

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
                status = response.json()["status"]
                
                # Checking the status to print the correct message
                if status == "pulled":
                    print(f"Model {model_type}, Number {number}: {status}, awaiting confirmation")
                elif status == "confirmed":
                    print(f"Model {model_type}, Number {number}: {status}")
                else:
                    print(f"Model {model_type}, Number {number}: {status}")
                    
            else:
                print(response.json()["error"])
            
        except (ValueError, argparse.ArgumentError):
            print("Invalid input format. Please use the format MODEL-NUMBER, e.g., SYS-0001")

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
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Numbering CLI")
    parser.add_argument("--interactive", action="store_true", help="Enter interactive mode")
    args = parser.parse_args()
    if args.interactive:
        NumberingCLI().cmdloop()
    else:
        print("Run with --interactive to enter interactive mode or use the API endpoints directly.")
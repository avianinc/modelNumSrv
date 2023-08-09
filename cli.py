import argparse
import requests
import cmd
import configparser

# Read from the config file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = config.get('DEFAULT', 'HOST', fallback='localhost')
PORT = config.get('DEFAULT', 'PORT', fallback='5001')
BASE_URL = f"http://{HOST}:{PORT}"

class NumberingCLI(cmd.Cmd):
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

    def do_confirm(self, args):
        """Confirm the reservation of a specific number for a given model type."""
        model_type, number = args.split()
        response = requests.post(f"{BASE_URL}/confirm/{model_type}/{number}")
        print(response.json().get("status", "An error occurred."))

    def do_release(self, args):
        """Release a specific number for a given model type."""
        model_type, number = args.split()
        response = requests.post(f"{BASE_URL}/release/{model_type}/{number}")
        print(response.json().get("status", "An error occurred."))

    def do_search(self, args):
        """Search for a specific number for a given model type."""
        model_type, number = args.split()
        response = requests.get(f"{BASE_URL}/search/{model_type}/{number}")
        print(response.json().get("status", "An error occurred."))

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

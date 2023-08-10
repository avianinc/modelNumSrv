import argparse
import requests
import cmd
import configparser
import os

# Initial read from the config file
config = configparser.ConfigParser()
config.read('config.ini')

HOST = 'localhost'
PORT = config.get('DEFAULT', 'PORT', fallback='5001')
BASE_URL = f"http://{HOST}"

class NumberingCLI(cmd.Cmd):
    use_rawinput = True  # Add this line
    intro = "Welcome to the model numbering CLI. Type help or ? to list commands.\n"
    prompt = "(numbering) "

    def do_set_base_url(self, new_url):
        """Set a new base URL for the CLI."""
        global BASE_URL, PORT
        
        # Check if user explicitly specifies a port.
        if ':' in new_url.split("//")[-1]:
            BASE_URL, PORT = new_url.rsplit(':', 1)
        else:
            BASE_URL = new_url
            PORT = config.get('DEFAULT', 'PORT', fallback='5001')
        
        # Update the config.ini
        config['DEFAULT']['base_url'] = f"{BASE_URL}:{PORT}"
        config['DEFAULT']['port'] = PORT

        with open('config.ini', 'w') as configfile:  # Save the updated base URL and port to the config file
            config.write(configfile)

        print(f"Base URL set to: {BASE_URL}:{PORT}")

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
        url = f"{BASE_URL}:{PORT}/pull/{model_type}"
        # print(f"Trying to access: {url}")  # Diagnostic print
        try:
            response = requests.get(url)
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

    def postcmd(self, stop, line):
        """This method is called after any command."""
        if hasattr(self, '_connection_error'):
            print("Error: Could not establish a connection to the server. Please check the BASE URL and ensure the server is running.")
            delattr(self, '_connection_error')  # remove the flag to reset the state
        return stop

    def onecmd(self, line):
        """Execute one command."""
        try:
            return super(NumberingCLI, self).onecmd(line)
        except requests.exceptions.ConnectionError:
            self._connection_error = True  # set a flag indicating there was a connection error
        except KeyboardInterrupt:
            print("\nExiting CLI.")
            return True

    def do_exit(self, _):
        """Exit the CLI."""
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Numbering CLI")
    parser.add_argument("--interactive", action="store_true", help="Enter interactive mode")
    args = parser.parse_args()
    if args.interactive:
        try:
            NumberingCLI().cmdloop()
        except requests.exceptions.ConnectionError:
            print("Error: Could not establish a connection to the server. Please check the BASE URL and ensure the server is running.")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nExiting CLI.")
    else:
        print("Run with --interactive to enter interactive mode or use the API endpoints directly.")

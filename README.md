# Model Numbering Service

Welcome to the Model Numbering Service. This system offers an automated solution for managing model numbers through a Flask API. The system comprises a server (`model_numbering_service.py`) interacting with a SQLite database (`model_numbers.db`), and a CLI (`numbCLI.py`) allowing users to easily manage model numbers.

## Overview:

1. **Server:** The heart of the system, running a Flask API to handle CRUD operations on model numbers.
2. **CLI:** A user-friendly command-line interface to communicate with the server and manage model numbers.
3. **Database:** A SQLite database (`model_numbers.db`) that persistently stores the model numbers and their states.
4. **Config File:** A configuration file (`config.ini`) that specifies settings, such as the port the server should run on.

## Getting Started:

### Prerequisites:

- Docker installed on your machine (optional for local setup).

### Setup:

1. **Configuration File:** The system uses a configuration file named `config.ini` for settings. Confirm this file is correctly set up with the desired port:

```ini
[DEFAULT]
PORT = 5001
```

Replace `5001` with your preferred port if necessary.

2. **Building the Docker Image (Docker setup):**

Navigate to the project's root directory and execute:

```bash
docker build -t model-numbering-service .
```

This builds a Docker image titled `model-numbering-service`.

3. **Running the Docker Container (Docker setup):**

After creating the image, start the server inside a Docker container with:

```bash
docker run -d -p 5001:5001 model-numbering-service
```

Substitute `5001:5001` with `<host_port>:<container_port>` if you adjusted the port in `config.ini`.

4. **Local Setup (Without Docker):**

Ensure you have Flask and the necessary dependencies installed. Then, simply run:

```bash
python model_numbering_service.py
```

### Usage:

**Server:** Once the Docker container is active, the Flask server will be ready and awaiting requests.

**CLI:** The `numbCLI.py` script offers a command-line interface to liaise with the server. Go to the CLI's directory and enter:

```bash
python numbCLI.py --interactive
```

This initiates the interactive CLI session, where you can add model types, list them, retrieve numbers, confirm numbers, and more.

### Commands with Examples:

Here's a quick overview of the available commands with examples:

- **Adding a Model Type**
  ```bash
  add_model_type SYS
  ```
  This adds a new model type named "SYS" for systems.

- **Listing Model Types**
  ```bash
  list_model_types
  ```

- **Pulling a Number for a Model Type**
  ```bash
  pull SYS
  ```
  This retrieves and reserves the next available number for the "SYS" model type.

- **Confirming a Specific Number**
  ```bash
  confirm SYS-0001
  ```

- **Releasing a Specific Number**
  ```bash
  release SYS-0001
  ```

- **Searching for a Specific Number's Status**
  ```bash
  search SYS-0001
  ```

- **Exiting the CLI**
  ```bash
  exit
  ```

Use `help` or `?` to see descriptions and guidance for each command.

---

## Executable CLI:

For ease of use, especially for those unfamiliar with Python or who prefer not to run scripts directly, an executable version of the CLI named `numcli.exe` has been provided in the `dist` folder. Run this file with the ```--interactive``` command. 

Build the cli using the command ```pyinstaller --onefile --name numbcli numbCLI.py```

### Using the Executable:

1. Navigate to the `dist` folder.
2. From a command prompt `.\numcli.exe --interactive` or run it from the command line.
3. This will start the CLI and you can use it as you would with the script version.

Remember, even if using the executable, ensure the server (Flask API) is running either locally or in the Docker container.

---

## Final Thoughts:

Make sure the server (Flask API) is running before attempting to use the CLI. The `model_numbers.db` database will be auto-generated when the server initiates for the first time.

Always inspect the `config.ini` for potential configuration alterations, especially if deploying in various environments.

---


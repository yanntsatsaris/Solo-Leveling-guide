# Solo-Leveling-guide

## Installation

### System Dependencies

Before running the application, you need to install the following system dependencies:

```bash
sudo apt-get update && sudo apt-get install -y libldap2-dev libsasl2-dev libssl-dev
```

### Python Dependencies

Install the required Python packages using pip and the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Configuration

Copy the `static/Conf/config.ini.example` to `static/Conf/config.ini` and update the values to match your environment.

### Running the application

To run the application, execute the following command:

```bash
python app.py
```

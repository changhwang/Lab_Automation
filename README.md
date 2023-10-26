## AAMP User Interface

### An app to control the automated additive manufacturing platform.

#### Installation

To use this app, you need to install Python (version 3.10 or higher).

In a terminal window in a new directory, run `pip install aamp_app` or `pip install --upgrade aamp_app` to install the app. Use the latter one to upgrade the app after it's installed. All dependencies will be installed with it. You may wish to use a virtual python environment if you don't want this app or its dependencies to interfere with your current system. On Mac or Linux-based systems, do this by running the following commands before installing:

`pip install virtualenv`: This line installs the virtualenv package which allows you to create virtual python environments.

`virtualenv venv`: This line creates a virtual environment (called `venv`) in the current directory. This will create a new folder (called `venv`) with the environment data.

`source venv/bin/activate`: This line activates the virtual environment. After activating the virtual environment, you should be able to see `(venv)` in your terminal window. If you close the terminal window/tab, you will have to execute this command to activate the environment again before using the app.

#### Usage

To start the app, run `aamp_app`. Enter the database user credentials for MongoDB. These credentials will be saved as plain text in a text file (called `pw.txt`) in the same directory. Therefore, this app should only be used on trusted computers. If the connection to the database cannot be established using the provided credentials, you will be required to run `aamp_app` again to retry. To delete the user credentials, simply delete the `pw.txt` file.

#### Device Requirements

Most devices should be able to connect to the app without any problems. However, certain devices require some drivers/software to create a connection. Due to the nature of the specific drivers/software, they must be installed separately.

-   [Thorlabs Devices (APT or Kinesis)](https://www.thorlabs.com/software_pages/viewsoftwarepage.cfm?code=Motion_Control)

### Project Structure

`aamp/` - Dash app entry

`aamp/devices/` - Device modules. All device modules inherit the `Device` class from `device.py`. If the device is a serial device, the module would inherit the `SerialDevice` class. Similarly, Arduino-based serial devices inherit the `ArduinoSerialClass` class.

`aamp/commands/` - Command modules. All command modules inherit the `Command` class from `command.py`. Examples for both commands and devices are given for dummy devices.

`aamp/pages/` - Pages for the dashboard. Developed using [Dash by Plotly](https://dash.plotly.com/).

`aamp/aamp_app.py` - Home page. Contains code to check for database credentials stored locally.

`aamp/mongodb_helper.py` - MongoDB helper functions.

`aamp/command_invoker.py` - Used to invoke recipes.

`aamp/command_sequence.py` - Used to manage recipes. Class contains functions to modify recipes.

`aamp/console_interceptor.py` - Used to get console messages to pass to dashboard components.

`aamp/util.py` - Helper functions and device definitions. All devices and their commands need to be defined in the `devices_ref_redundancy` dictionary.

### Miscellaneous Commands (for dev)

Package app:

`python3 setup.py sdist bdist_wheel`

Upload to pip:

`twine upload --skip-existing dist/*`

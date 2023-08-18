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

#### Miscellaneous Commands (for dev)

Package app:

`python3 setup.py sdist bdist_wheel`

Upload to pip:

`twine upload --skip-existing dist/*`

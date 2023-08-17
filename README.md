## AAMP User Interface
#### An app to control the automated additive manufacturing platform.

Use `pip install aamp_app` or `pip install --upgrade aamp_app` to install the app. All dependencies should be installed with it.

To start the app, run `aamp_app`. Enter the database user credentials for MongoDB. These credentials will be saved in a text file in the same directory as plain text. Therefore, do not use on public computers.


Package app:

`python3 setup.py sdist bdist_wheel`

Upload to pip:

`twine upload --skip-existing dist/*`

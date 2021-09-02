# LabAutomation
LabAutomation is a modular framework for automating multiple devices or instruments capable of being controlled through Python. 

## Description
LabAutomation was developed for the purpose of automating laboratory experiments to enable high-throughput data collection and process optimization. It can automate experimental procedures that involve instruments from different vendors, with different communication protocols, and also home-built equipment. The automated procedures can then be tied into sequential model-based optimization algorithms (e.g. Bayesian optimization) to enable self-driving, autonomous lab experiments.

LabAutomation implements the command pattern in order to execute a command sequence, or 'recipe'. Generally, each command interacts with a device, or 'receiver',  by calling its methods to control the actual physical device. Several devices and commands have already been implemented (see below). However, as long as you can write commands for your device in Python it can easily be used in conjunction with other devices due to the modular nature of the command pattern. Further details on the program structure and how to create new devices, commands, and recipes are shown below. 

Here are some features of the program:
- Saving and loading of recipes to .yaml files
- Looping of recipe sub-sections for repeated procedures or for parametric sweeps
- Creation of sub-recipes or more complex commands through the use of composite commands
- Recipe pausing for semi-automated recipes that require manual actions in between commands
- Logging of all command details and their execution result
- Slack channel notification and log file upload when command execution encounters an error

## Supported Devices
The following devices have tested receiver and command modules:
- Newport stages controlled by ESP-301/ESP-302 motion controllers
- StellarNet Spectrometers (multiple spectrometers and spectra merging supported)
- Ximea cameras
- Arduino-based stepper motor(s) (click here for materials, schematic, and code)
- Arduino-based PID controlled resistive heater (click here for materials, schematic, and code)

The following devices are planned to be added:
- Kinova gen7 robot arm
- IKA hot/stir plates
- Hamilton PSD/6 syringe pump
- Shutter and lamp control for StellarNet Spectrometers
- More to come...

## Getting Started
### Requirements
This package was developed using Python 3.8. 
The required packages are listed below. The versions used during developement are indicated in parenthesis. If a specific version is required it will be indicated.
- The core framework only requires PyYaml (5.4.1)
- Slack notifications are optional and require slackclient (2.9.3)
- The recipe_tool.py text-based UI requires questionary (1.10.0) and colorama (0.4.4)
- Any device that communicates via serial requires PySerial (3.5)
- StellarNet spectrometers:
    - NumPy (1.20.3)
    - Pandas (1.3.1)
    - SciPy (1.7.0)
    - pyusb (1.0.0b1 required)
    - [stellarnet_driver file from vendor](https://www.stellarnet.us/software/spectrometer-python-application-driver/)
- Ximea cameras:
    - [xiAPI](https://www.ximea.com/support/wiki/apis/Python)
    - Pillow (8.3.1)

To run example 6 which combines automation with Bayesian optimization you will need:
- NumPy
- Matplotlib
- Pandas
- Scikit-Optimize

### Installation
Download the repository and create a recipe using a script or the recipe_tool.py UI. See Usage for examples.

## Usage
### Automation
The general workflow is as follows:
- If not created, create the receiver and command modules for your device
- Create a command sequence
- Add devices you plan to use to the command sequence
- Add commands to the command sequence
- Create a command invoker and pass it the sequence during construction
- Invoke the commands to execute them

There are three ways to create and modify the command sequence:
1. Use a .py script to create the command sequence (recommended)
2. Use the recipe_tool.py text-based UI (recommended for simple recipes only)
3. For a saved sequence, you can edit the .yaml file directly (recommended for small modifications only)

The first method is recommended. Please go through the example scripts 1 to 5 in the examples folder to learn how they work. The examples use fake devices (DummyHeater and DummyMotor) and commands so you do not need to have actual hardware to run the examples.
Run the examples from root using:
```
python -m examples.example#
```

For the second method you can use run the text-based UI tool from root using:
```
python recipe_tool.py
```
You can start creating and executing recipes with the DummyHeater and DummyMotor devices. You can also load an example recipe from recipes/ui_recipe_example.yaml. Note that the recipe_tool UI does not currently support CompositeCommands.

For the third method you can inspect any of the recipe .yaml files and make changes to them (except for example1.yaml as it is loaded in example2)

### Autonomous Process Optimization
Example 6 demonstrates a method of combining automated recipes with Bayesian optimization using scikit's optimize package. Please see their Optimizer or gp_minimize examples to get familiar with the workflow. Example 6 emulates optimization of a material processing experiment. It uses a fake measurement device (DummyMeter) that 'measures' some property from a random noisy objective function surface that depends on a DummyHeater's temperature and a DummyMotor's speed. You can think of it as corresponding to some process like 3d printing or ink coating (i.e. What printing temperature and speed gives me the best material property?). You will need some more packages to run example 6 (listed above).

## Further Details
To do
As a general overview, the physical devices need to be controlled by Python at some level through a 'receiver' module. Commands are then written for each device, or 'receiver'. Commands for different receivers are then put together into a sequence. The sequence is then passed to the invoker which iterates through the sequence and executes each command.

## License
To do


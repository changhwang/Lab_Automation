# Example 1: Create a basic command sequence
# run from root using 'python -m examples.example1'

##################################################
##### Import necessary classes
##################################################
# Import the CommandSequence class
from command_sequence import CommandSequence
# Import the CommandInvoker class if you plan to execute the commands
from command_invoker import CommandInvoker

# Import the devices that will be used
from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor
# Import the command modules that will be used
from commands.dummy_heater_commands import *
from commands.dummy_motor_commands import *

##################################################
##### Initialize an empty command sequence
##################################################
seq = CommandSequence()

##################################################
##### Add devices (aka receivers) to the command sequence
##################################################
# The order you add devices does not matter

# Instantiate heater1 and add to sequence
heater1 = DummyHeater('heater1') # the variable name and name string do not have to be the same, but it is recommended
seq.add_device(heater1)
# Instantiate motor1 and add to sequence
motor1 = DummyMotor('motor1')
seq.add_device(motor1)
# You can also directly add an instance to the sequence
seq.add_device(DummyMotor('motor2'))

##################################################
##### Add commands to the command sequence
##################################################
# The order of the commands does matter! (They will be executed sequentially starting from index 0)
# use seq.add_command to add a command at a particular index in the sequence
# if the index is not specified, the command is appended to the end

# First add any commands to connect to the devices
# - Some devices need to be explicitly connected to, e.g. serial devices
# - Some devices don't need to be explicitly connected to, e.g. some USB devices
# Then add any commands to initialize the devices
seq.add_command(DummyHeaterInitialize(heater1))
seq.add_command(DummyMotorInitialize(motor1))
# If you added the device directly as done for 'motor2' then it does not have a named variable.
# You can access it using the dict seq.device_by_name
seq.add_command(DummyMotorInitialize(seq.device_by_name['motor2'])) 

# Next add commands for your actual process
# Every command has an optional delay argument
# if delay='P', the command will require an input before continuing
# if delay=1.0, the command will delay for 1.0 second before continuing
# if delay is not specified, there will be no delay
# If you want to use an explicit command for a delay or pause, 
#   then you can use DelayPauseCommand imported from commands.utility_commands

seq.add_command(DummyHeaterSetTemp(heater1, 60.0))
seq.add_command(DummyMotorSetSpeed(motor1, 10.0, delay=3.0))
seq.add_command(DummyMotorMoveAbsolute(motor1, 30.0))
seq.add_command(DummyMotorMoveRelative(motor1, -20.0))

seq.add_command(DummyHeaterDeinitialize(heater1))
seq.add_command(DummyMotorDeinitialize(motor1))
seq.add_command(DummyMotorDeinitialize(seq.device_by_name['motor2']))

##################################################
##### You can save the recipe to a yaml file
##################################################
recipe_file = 'recipes/example1.yaml'
seq.save_to_yaml(recipe_file)

##################################################
##### Initialize command invoker with the sequence and args
##################################################
# Once the sequence is finalized, pass it to the invoker during construction
# You can also choose to log the execution details to a file (default True)
# You can specify the log filename (default None will use a timestamp as the filename and create it in logs/)
# You can choose to alert a slack channel if there is an error (default False)
# - if you do not have the slackclient package then leave it False
# - if you want to alert slack, you need to: 
#       1) install the slackclient package in your environment
#       2) create a slack bot online and get the bot's token
#       3) store the token as an environmental variable (see CommandInvoker)
#       4) edit the channel you want the bot to message (see CommandInvoker)
log_file = 'logs/example1.log'
invoker = CommandInvoker(seq, log_to_file=True, log_filename=log_file, alert_slack=False) 

##################################################
##### Invoke all the commands in the sequence by calling their execute method
##################################################
# Let's double check the recipe before continuing
seq.print_command_names()

userinput = input("\ntype 'y' to continue, type anything else to quit: ")
if userinput == 'y':
    # Invoke the command sequence!
    invoker.invoke_commands()



# Example 2: Load and edit a command sequence (aka recipe)
# run from root using 'python -m examples.example2'

from command_sequence import CommandSequence
from command_invoker import CommandInvoker

from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor
from commands.dummy_heater_commands import *
from commands.dummy_motor_commands import *

# Create new sequence
seq = CommandSequence()

# Load the command sequence saved by example1
recipe_file = 'recipes/example1.yaml'
seq.load_from_yaml(recipe_file)

# You can remove a device
seq.remove_device('motor2')
# If you remove a device you should remove all commands that reference it
seq.remove_command(index=9)

# You can insert a command at a particular index
# This will be our new first command after initialization
seq.add_command(DummyHeaterSetHeatRate(seq.device_by_name['heater1'], 20.0, delay='P'), index=3)

# You can move commands to a different index
# (This can be confusing if the sequence is created/modified in a non-sequential way)
# (This is mainly for the recipe_tool.py UI) 
seq.move_command_by_index(old_index=9, new_index=8) # move motor1 deinitialization to before heater1

# Save the modified recipe 
new_recipe_file = 'recipes/example2.yaml'
seq.save_to_yaml(new_recipe_file)

# Instantiate command invoker
log_file = 'logs/example2.log'
invoker = CommandInvoker(seq, log_to_file=True, log_filename=log_file, alert_slack=False) 

# Let's double check the recipe before continuing
seq.print_command_names()

userinput = input("\ntype 'y' to continue, type anything else to quit: ")
if userinput == 'y':
    # Invoke the command sequence!
    invoker.invoke_commands()



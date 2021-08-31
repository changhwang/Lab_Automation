# Example 3: Loop over a subsection of a command sequence 
# run from root using 'python -m examples.example3'

from command_sequence import CommandSequence
from command_invoker import CommandInvoker

from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor
from commands.dummy_heater_commands import *
from commands.dummy_motor_commands import *

# Create new sequence
seq = CommandSequence()

# Add devices
heater1 = DummyHeater('heater1')
seq.add_device(heater1)
motor1 = DummyMotor('motor1')
seq.add_device(motor1)

# Add commands
seq.add_command(DummyHeaterInitialize(heater1))
seq.add_command(DummyMotorInitialize(motor1))

# We will add a looped section that will be repeated, only 1 looped section is allowed at the moment
# Mark the start of the looped section
# This can be done using either:
# - seq.add_loop_start()
# - seq.add_command(LoopStartCommand()) (This requires you to import from commands.utility_commands)
seq.add_loop_start() # this counts as a command and is therefore at index 2
seq.add_command(DummyHeaterSetTemp(heater1, 60.0))
seq.add_command(DummyMotorMoveRelative(motor1, 20.0))
seq.add_command(DummyHeaterSetTemp(heater1, 25.0))
seq.add_command(DummyMotorMoveRelative(motor1, -20.0))

# Mark the end of the looped section
seq.add_loop_end()

seq.add_command(DummyHeaterDeinitialize(heater1))
seq.add_command(DummyMotorDeinitialize(motor1))

# We can specify how many times the looped section should iterate
# It must be an integer, at least 1 or greater (
#   - a value of 1 means it executes only once as if the loop marker commands did not exist
# It can also be the string 'ALL' (This is the default value. More on this in later examples)
seq.num_iterations = 3 

# Save recipe to file
recipe_file = 'recipes/example3.yaml'
seq.save_to_yaml(recipe_file)

# Create invoker
log_file = 'logs/example3.log'
invoker = CommandInvoker(seq, log_to_file=True, log_filename=log_file, alert_slack=False) 

# We can display the recipe with the loop markers
print("\n--Recipe with loop marker commands--")
seq.print_command_names()
# Or we can display the unlooped recipe with all iterations "unlooped" into one list
print("\n--Recipe with unlooped commands--")
seq.print_unlooped_command_names()

userinput = input("\ntype 'y' to continue, type anything else to quit: ")
if userinput == 'y':
    # Invoke the command sequence!
    invoker.invoke_commands()



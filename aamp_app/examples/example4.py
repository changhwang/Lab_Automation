# Example 4: Loop with changing commands on each iteration
# run from root using 'python -m examples.example4'

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

seq.add_loop_start()
# Each element in the command sequence is actually a list containing commands corresponding to each loop iteration
# So far in the previous examples, each element was actually a list containing only a single command
# If we want the command to change on each iteration, then we can add commands to this iteration list
# This can be done in two ways:
# 1) When we first add a command to the command sequence, we can add a list instead of a single command
#      - The list is then treated as an iteration list
# Let's add a DummyHeaterSetTemp command where the temperature changes on each iterations for 4 iterations
initial_temp_commands = [
    DummyHeaterSetTemp(heater1, 40.0),
    DummyHeaterSetTemp(heater1, 50.0),
    DummyHeaterSetTemp(heater1, 60.0),
    DummyHeaterSetTemp(heater1, 70.0),
]
seq.add_command(initial_temp_commands)

# The second way to add command iterations is for pre-existing commands:
# 2) We can use the seq.add_command_iteration method to add an iteration at a particular command index and at a particular iteration index
#       - If either index is None (default) then it will be appended
# Let's add a single command with no iterations like normal to set the motor speed
seq.add_command(DummyMotorSetSpeed(motor1, 10.0)) 
# Now let's append iterations for this command
seq.add_command_iteration(DummyMotorSetSpeed(motor1, 20.0)) # Iteration 2 at iteration index 1
seq.add_command_iteration(DummyMotorSetSpeed(motor1, 30.0)) # Iteration 3 at iteration index 2
seq.add_command_iteration(DummyMotorSetSpeed(motor1, 40.0)) # Iteration 4 at iteration index 3


# Rest of the recipe
seq.add_command(DummyMotorMoveRelative(motor1, 20.0))
seq.add_command(DummyHeaterSetTemp(heater1, 25.0))
seq.add_command(DummyMotorMoveRelative(motor1, -20.0))
seq.add_loop_end()

seq.add_command(DummyHeaterDeinitialize(heater1))
seq.add_command(DummyMotorDeinitialize(motor1))

# Specify number of loop iterations
seq.num_iterations = 5
# What if the number of iterations is greater that a command's iteration list length?
# During execution when the current iteration surpasses the iteration list length then the last iteration will be used.
# For example, on the 5th iteration, the heater will be set to 70 again and the motor speed will be set to 40 again (see the unlooped printed names)
# This explains why in example3.py, we were able to repeat the looped section even though there were no iterations
# So if a command within the looped section does not need to change, you only need to add it once (like the MoveRelative and SetTemp to 25 commands above)

# !!!!!!! If you just want to make the number of iterations equal the largest iteration list length in your recipe,
# then set num_iterations to 'ALL' (This is the default value when a sequence is created)

# Additional notes:
# - The iterations for a particular command do NOT need to be of the same command type
# - The iterations for a particular command do NOT need to correspond to the same device or device type
# - The num_iterations is at least 1 for no looping, but remember indices start from 0 so when adding an iteration the first iteration is at index 0
#       - on the second iteration, the command at iteration index 1 is executed
#       - on the third iteration, the command at iteration index 2 is executed...
# - For large parametric sweeps, you can use for loops to add iterations to the recipe
# - At the moment, only 1 looped section is allowed for the recipe

# Save recipe to file
recipe_file = 'recipes/example4.yaml'
seq.save_to_yaml(recipe_file)

# Create invoker
log_file = 'logs/example4.log'
invoker = CommandInvoker(seq, log_to_file=True, log_filename=log_file, alert_slack=False) 

# Display the recipe with the loop markers
print("\n--Recipe with loop marker commands--")
seq.print_command_names()
# Display the unlooped recipe with all iterations "unlooped" into one list
print("\n--Recipe with unlooped commands--")
seq.print_unlooped_command_names()

userinput = input("\ntype 'y' to continue, type anything else to quit: ")
if userinput == 'y':
    # Invoke the command sequence!
    invoker.invoke_commands()



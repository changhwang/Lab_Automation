# Example 5: Creating and using composite commands
# run from root using 'python -m examples.example5'

from command_sequence import CommandSequence
from command_invoker import CommandInvoker

from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor
from commands.command import CompositeCommand
from commands.dummy_heater_commands import *
from commands.dummy_motor_commands import *
from commands.dummy_composite_commands import *

# Create new sequence
seq = CommandSequence()

# Add devices
heater1 = DummyHeater('heater1')
seq.add_device(heater1)
motor1 = DummyMotor('motor1')
seq.add_device(motor1)
motor2 = DummyMotor('motor2')
seq.add_device(motor2)

# Add commands
seq.add_command(DummyHeaterInitialize(heater1))
seq.add_command(DummyMotorInitialize(motor1))
seq.add_command(DummyMotorInitialize(motor2))

# A Composite command allows you to group together multiple commands into one command
# This effectively allows you to make more complex, higher level commands or sub-recipes
# A CompositeCommand behaves like a regular command to any object that uses it
# e.g. It has an execute method as well as a was_successful boolean and a result_message string like a regular command
# A composite command maintains a list of internal commands, from which commands can be added to or removed from
# When a composite command is executed, it goes through each command in its list and executes them sequentially
# When an internal command finishes execution, the composite command gets the command's success bool and result message and copies it into its own
# If an internal command executed with a failed result, the composite command stops execution
# Since logging is handled by the invoker, you will either see the success of the composite's last command or you will see the failure of a command

# You can create composite commands in two ways:
# 1) If this is a one-off, then you can simply create it in the script
# 2) If it is a useful composite command that may be used again then create it in the command module
#       - a) If the composite only uses devices of a single type, add it to that device's command module
#       - b) If the composite uses devices of multiple types, then create a new command module with a relevant name
# We will demonstrate all of the above here

# Option 1) (create a one-off composite command)
# Create a two-step movement motor command
DummyMotorDoubleMove = CompositeCommand()
DummyMotorDoubleMove.add_command(DummyMotorSetSpeed(motor1, 10.0))
DummyMotorDoubleMove.add_command(DummyMotorMoveRelative(motor1, 20.0))
DummyMotorDoubleMove.add_command(DummyMotorSetSpeed(motor1, 15.0))
DummyMotorDoubleMove.add_command(DummyMotorMoveRelative(motor1, 30.0))
# add it to the sequence
seq.add_command(DummyMotorDoubleMove)

# Option 2a) (create a composite command that works with devices of a single type)
# Example #1: Define a composite command for a DummyMotor that temporarily changes its speed, then performs a move, then reverts the speed to its original value
# See DummyMotorMoveSpeedAbsolute in commands/dummy_motor_commands.py 
seq.add_command(DummyMotorMoveSpeedAbsolute(motor1, 50.0, 0.0))
# Example #2: Define a composite command that moves a list of motors to a list of positions at a particular speed
# See DummyMotorMultiMoveAbsolute in commands/dummy_motor_commands.py 
seq.add_command(DummyMotorMultiMoveAbsolute([motor1, motor2], [10.0, 20.0], 5.0))
seq.add_command(DummyMotorMultiMoveAbsolute([motor1, motor2], [5.0, 5.0], 20.0))
# Example #3: Define a heating schedule that ramps a DummyHeater to temperature1 at rate1, holds for a specified time, then ramps to temperature2 at rate2
# See DummyHeaterRampHoldRamp in commands/dummy_heater_commands.py 
seq.add_command(DummyHeaterRampHoldRamp(heater1, 30.0, 20.0, 5.0, 60.0, 10.0))

# Option 2b) (create a composite command that works with devices of multiple types)
# Define a composite command that:
# 1) sets a DummyHeater to specified temperature at specified rate
# 2) moves a DummyMotor by a relative distance forward and then backward, 
# 3) sets the DummyHeater to 25 
# 4) reverts the heat_rate and speed to their original values
# See DummyPrinterHeatMove in commands/dummy_composite_commands.py
seq.add_command(DummyPrinterHeatMove(heater1, motor2, 85.0, 20.0, 35.0, 10.0))

# Rest of the recipe
seq.add_command(DummyHeaterDeinitialize(heater1))
seq.add_command(DummyMotorDeinitialize(motor1))
seq.add_command(DummyMotorDeinitialize(motor2))


# Save recipe to file
recipe_file = 'recipes/example5.yaml'
seq.save_to_yaml(recipe_file)

# Create invoker
log_file = 'logs/example5.log'
invoker = CommandInvoker(seq, log_to_file=True, log_filename=log_file, alert_slack=False) 

# Display the recipe
seq.print_command_names()

userinput = input("\ntype 'y' to continue, type anything else to quit: ")
if userinput == 'y':
    # Invoke the command sequence!
    invoker.invoke_commands()



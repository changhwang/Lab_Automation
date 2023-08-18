import sys
import inspect
from os import listdir
from os.path import isfile, join
import importlib
import copy

try:
    import serial.tools.list_ports
except ImportError:
    _has_serial = False
else:
    _has_serial = True
import questionary
from colorama import init
from colorama import Fore, Back, Style

init()

from aamp_app.command_sequence import CommandSequence
from aamp_app.command_invoker import CommandInvoker
from aamp_app.commands.command import Command
from aamp_app.commands.utility_commands import LoopStartCommand, LoopEndCommand
from aamp_app.devices.heating_stage import HeatingStage
from aamp_app.devices.multi_stepper import MultiStepper
from aamp_app.devices.newport_esp301 import NewportESP301

# from devices.stellarnet_spectrometer import StellarNetSpectrometer
# from devices.ximea_camera import XimeaCamera
from aamp_app.devices.dummy_heater import DummyHeater
from aamp_app.devices.dummy_motor import DummyMotor

import aamp_app.util as util


# TODO
# Clean up comments
# some refactoring of duplicate code
# type hinting
# add compatibility with composite and utility commands (try to avoid coding speciific class dependencies)

# ================ Constants =============================
named_devices = util.named_devices
command_directory = "commands/"
load_directory = "recipes/user_recipes/"
save_directory = "recipes/user_recipes/"
log_directory = "logs/"
# data directory?
custom_style = questionary.Style([("highlighted", "bold"), ("pointer", "fg:#00ff00")])


seq = CommandSequence()


# seq.load_from_yaml('test.yaml')
def main():
    print_intro()
    main_menu()


##################################################
# Main Menu
##################################################
def main_menu():
    while True:
        main_menu_prompt = "Main Menu - Choose an option:"
        main_menu_options = {
            "New/Save/Load Recipe": recipe_menu,
            "Display Recipe Info": display_menu,
            "Edit Devices": device_menu,
            "Edit Commands": command_menu,
            "Edit Command Iterations": iteration_menu,
            "Execute Recipe": execute_recipe,
            "Manual Command Session": execute_manual,
            "Help": print_help,
            "Quit": quit_program,
        }
        prompt = questionary.select(
            main_menu_prompt, choices=list(main_menu_options.keys()), style=custom_style
        )
        response = prompt.ask()
        response_function = main_menu_options[response]
        response_function()


##################################################
# New/Save/Load Recipe Menu
##################################################
def recipe_menu():
    recipe_menu_prompt = "Choose an option:"
    recipe_menu_options = {
        "Save Recipe": save_sequence,
        "Load Recipe": load_sequence,
        "New Recipe": clear_sequence,
        "Back to Main Menu": main_menu,
    }
    prompt = questionary.select(
        recipe_menu_prompt, choices=list(recipe_menu_options.keys()), style=custom_style
    )
    response = prompt.ask()
    response_function = recipe_menu_options[response]
    response_function()


def clear_sequence():
    response = questionary.confirm(
        "Create new recipe. Any unsaved data will be lost. Continue?",
        default=False,
        style=questionary.Style(
            [
                ("question", "fg:#ff0000"),
            ]
        ),
    ).ask()
    if response:
        global seq
        seq = CommandSequence()
        print(Fore.GREEN + "New recipe created!")
    else:
        print(Fore.RED + "Did not create new recipe!")


def save_sequence():
    save_file = questionary.path(
        "Enter the file you would like to save to or type 'quit':",
        default=save_directory,
        validate=lambda file: valid_save_file(file, save_directory),
        style=custom_style,
    ).ask()

    if save_file == "quit":
        return

    if isfile(save_file):
        response = questionary.confirm(
            "File already exists. Overwrite file?",
            default=False,
            style=questionary.Style(
                [
                    ("question", "fg:#ff0000"),
                ]
            ),
        ).ask()
        if response:
            seq.save_to_yaml(save_file)
            print(Fore.GREEN + "Recipe has been saved to '" + save_file + "'!")
        else:
            print(Fore.RED + "Recipe has not been saved to file!")
    else:
        seq.save_to_yaml(save_file)
        print(Fore.GREEN + "Recipe has been saved to '" + save_file + "'!")


def load_sequence():
    prompt = questionary.path(
        "Enter the recipe file you would like to load or type 'quit':",
        default=load_directory,
        validate=lambda file: valid_yml(file),
    )
    yaml_file = prompt.ask()

    if yaml_file.lower() == "quit":
        return

    # Load the yml file data into the sequence
    global seq
    seq = CommandSequence()
    seq.load_from_yaml(yaml_file)
    print(Fore.GREEN + "Recipe from yaml file loaded!")


##################################################
# Display Menu
##################################################
def display_menu():
    while True:
        display_menu_prompt = "Display Menu - Choose an option:"
        display_menu_options = {
            "Display Devices": display_device_menu,
            "Display Commands": display_commands,
            "Display Commands (Hide Iterations)": display_commands_hide_iterations,
            "Display Commands (Unlooped)": display_commands_unlooped,
            "Display a Command's Iterations": display_command_iterations,
            "Back to Main Menu": main_menu,
        }
        prompt = questionary.select(
            display_menu_prompt,
            choices=list(display_menu_options.keys()),
            style=custom_style,
        )
        response = prompt.ask()
        response_function = display_menu_options[response]
        response_function()


def display_device_menu():
    if len(seq.device_list) == 0:
        print(Fore.RED + "There are currently no devices added to the recipe.")
        return
    while True:
        display_device_menu_prompt = "Choose a device to see more details:"
        print_devices()
        device_index = select_device(display_device_menu_prompt)
        if device_index is None:
            break
        else:
            display_device_properties(device_index)


def print_devices():
    device_names_classes = (
        seq.get_device_names_classes()
    )  # [name, class name] of every device
    print("")
    print(Fore.WHITE + "List of Devices:")
    print(Fore.GREEN + " {:20.20s}".format("Name") + Fore.YELLOW + "Class")
    for name_class in device_names_classes:
        print(
            Fore.GREEN
            + " {:20.20s}".format(name_class[0])
            + Fore.YELLOW
            + name_class[1]
        )
    print("")


def display_device_properties(device_index: int):
    attr_dict = seq.device_list[device_index].__dict__
    print("")
    print(
        Fore.WHITE
        + "List of device properties for: "
        + Fore.GREEN
        + seq.device_list[device_index].name
    )
    for name, value in attr_dict.items():
        print(Fore.WHITE + " {:20.20s}".format(name) + " = " + Fore.YELLOW + str(value))
    print("")
    print(Fore.WHITE + "Press ENTER to continue")
    input()


def display_commands():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands added to the recipe.")
        return
    command_names = seq.get_command_names()
    print("")
    print(Fore.WHITE + "List of Commands:")
    print(
        Fore.RED
        + "{:7s}".format("Index")
        + Fore.CYAN
        + "{:40s}".format("Command Class")
        + Fore.GREEN
        + Fore.WHITE
        + "Parameters"
    )
    index = 0
    for name in command_names:
        name_parts = name.strip().split(" ")

        if "IterIndex" in name_parts[0]:
            print(Fore.RED + "{:7s}".format(" "), end="")
            print(Fore.WHITE + "{:12.12s}".format(name_parts.pop(0)), end="")
            print(Fore.CYAN + "{:28.28s}".format(name_parts.pop(0)), end="")
        else:
            print(Fore.RED + "{:7s}".format(str(index)), end="")
            index += 1
            print(Fore.CYAN + "{:40.40s}".format(name_parts.pop(0)), end="")
        if len(name_parts) == 0:
            print("")
        else:
            for param in name_parts:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                print(
                    Fore.WHITE + param_name + "=" + Fore.YELLOW + param_value, end=" "
                )
            print("")
    print("")


def display_commands_hide_iterations():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands added to the recipe.")
        return

    command_names = seq.get_command_names()
    for ndx, name in enumerate(command_names):
        if "IterIndex" in name:
            command_names[ndx - 1] = "*" + command_names[ndx - 1]
    for ndx, name in enumerate(command_names):
        while "IterIndex" in command_names[ndx]:
            del command_names[ndx]

    print("")
    print(Fore.WHITE + "List of Commands:")
    print(
        Fore.RED
        + "{:7s}".format("Index")
        + Fore.CYAN
        + "{:40s}".format("Command Class")
        + Fore.GREEN
        + Fore.WHITE
        + "Parameters"
    )
    index = 0
    for name in command_names:
        name_parts = name.strip().split(" ")
        print(Fore.RED + "{:7s}".format(str(index)), end="")
        index += 1
        if "*" in name_parts[0]:
            print(
                Fore.WHITE
                + "*"
                + Fore.CYAN
                + "{:39.39s}".format(name_parts.pop(0)[1:]),
                end="",
            )
        else:
            print(Fore.CYAN + "{:40.40s}".format(name_parts.pop(0)), end="")
        if len(name_parts) == 0:
            print("")
        else:
            for param in name_parts:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                print(
                    Fore.WHITE + param_name + "=" + Fore.YELLOW + param_value, end=" "
                )
            print("")
    print("")


def display_commands_unlooped():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands added to the recipe.")
        return

    command_list = seq.get_unlooped_command_list()
    if len(command_list) == 0:
        print(
            Fore.RED
            + "The command sequence and/or num_iterations is not valid, cannot unloop."
        )
        return

    command_names = []
    for command in command_list:
        command_names.append(command.name)

    print("")
    print(Fore.WHITE + "List of Commands:")
    print(
        Fore.RED
        + "{:15s}".format("Unlooped Index")
        + Fore.CYAN
        + "{:40s}".format("Command Class")
        + Fore.GREEN
        + Fore.WHITE
        + "Parameters"
    )
    index = 0
    for name in command_names:
        name_parts = name.strip().split(" ")
        print(Fore.RED + "{:15s}".format(str(index)), end="")
        index += 1
        print(Fore.CYAN + "{:40.40s}".format(name_parts.pop(0)), end="")
        if len(name_parts) == 0:
            print("")
        else:
            for param in name_parts:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                print(
                    Fore.WHITE + param_name + "=" + Fore.YELLOW + param_value, end=" "
                )
            print("")
    print("")


def display_command_iterations():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands added to the recipe.")
        return

    index = select_command("Choose a command to view its iterations:")
    if index is None:
        return
    iteration_names = []
    for iteration in seq.command_list[index]:
        iteration_names.append(iteration.name)

    print("")
    print(Fore.WHITE + "List of Command Iterations:")
    print(
        Fore.RED
        + "{:16s}".format("Iteration Index")
        + Fore.CYAN
        + "{:40s}".format("Command Iteration Class")
        + Fore.GREEN
        + Fore.WHITE
        + "Parameters"
    )
    index = 0
    for name in iteration_names:
        name_parts = name.strip().split(" ")
        print(Fore.RED + "{:16s}".format(str(index)), end="")
        index += 1
        print(Fore.CYAN + "{:40.40s}".format(name_parts.pop(0)), end="")
        if len(name_parts) == 0:
            print("")
        else:
            for param in name_parts:
                param_name = param.split("=")[0]
                param_value = param.split("=")[1]
                print(
                    Fore.WHITE + param_name + "=" + Fore.YELLOW + param_value, end=" "
                )
            print("")
    print("")


##################################################
# Edit Device Menu
##################################################
def device_menu():
    while True:
        device_menu_prompt = "Device Menu - Choose an option:"
        device_menu_options = {
            "Display Devices": display_device_menu,
            "Add Device": add_device,
            "Remove Device": remove_device,
            "Display COM Port Info": print_com_port_info,
            "Back to Main Menu": main_menu,
        }
        prompt = questionary.select(
            device_menu_prompt,
            choices=list(device_menu_options.keys()),
            style=custom_style,
        )
        response = prompt.ask()
        response_function = device_menu_options[response]
        response_function()


def add_device():
    approved_devices = list(named_devices.keys())
    approved_devices.append("Go back")
    response = questionary.select(
        "Which approved device would you like to add?",
        choices=approved_devices,
        style=custom_style,
    ).ask()

    if response == "Go back":
        return
    if response in seq.device_by_name:
        print(
            Fore.RED
            + "Device is already added. To edit it, you must remove it and re-add it."
        )
        return
    device_cls = named_devices[response]
    arg_dict = prompt_signature_args(device_cls.__init__, ignored_args=["name"])
    arg_dict["name"] = response
    seq.add_device(device_cls(**arg_dict))
    print(Fore.GREEN + response + " was added to the device list")


def remove_device():
    if len(seq.device_list) == 0:
        print(Fore.RED + "There are currently no devices added to the recipe.")
        return
    device_index = select_device("Choose ONE device to remove:")
    if device_index is None:
        return
    name = seq.device_list[device_index].name
    response = questionary.confirm(
        "Are you sure you want to delete " + name + "?",
        default=False,
        style=questionary.Style(
            [
                ("question", "fg:#ff0000"),
            ]
        ),
    ).ask()
    if response:
        seq.remove_device_by_index(device_index)
        print(Fore.GREEN + name + " was removed from the device list")
    else:
        print(Fore.RED + name + " was NOT removed from the device list")


def print_com_port_info():
    if _has_serial:
        ports = serial.tools.list_ports.comports()
        print("")
        for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))
        print("")
    else:
        print(Fore.RED + "PySerial is not installed")


##################################################
# Edit Command Menu
##################################################
def command_menu():
    while True:
        command_menu_prompt = "Command Menu - Choose an option:"
        command_menu_options = {
            "Display Commands": display_commands,
            "Add Command": add_command,
            "Remove Command(s)": remove_commands,
            "Move Command": move_command,
            "Add Loop": add_loop,
            "Remove All Loops": remove_loops,
            "Back to Main Menu": main_menu,
        }
        prompt = questionary.select(
            command_menu_prompt,
            choices=list(command_menu_options.keys()),
            style=custom_style,
        )
        response = prompt.ask()
        response_function = command_menu_options[response]
        response_function()


def add_command():
    if len(seq.device_list) == 0:
        print(
            Fore.RED
            + "There are currently no devices. Add a device to create commands for it."
        )
        return

    device_index = select_device("Choose a device to create a command for:")
    if device_index is None:
        return
    device = seq.device_list[device_index]

    valid_command_dict = get_all_commands_classes_for_receiver(
        command_directory, device.__class__
    )
    valid_command_names_desc = []
    for name, cls in valid_command_dict.items():
        valid_command_names_desc.append("{:30.30s}".format(name) + "- " + cls.__doc__)
    valid_command_names_desc.append("Go back")

    response = questionary.select(
        "Choose the command to add:",
        choices=valid_command_names_desc,
        style=custom_style,
    ).ask()
    if response == "Go back":
        return
    command_class_name = response.split(" ")[0]
    command_class = valid_command_dict[command_class_name]

    arg_dict = prompt_signature_args(command_class.__init__, ["receiver"])
    arg_dict["receiver"] = device
    arg_dict["delay"] = prompt_delay()

    append_insert = questionary.select(
        "Append this command to the list or insert at a specific position?",
        choices=["Append", "Insert"],
        style=custom_style,
    ).ask()
    if append_insert == "Append":
        seq.add_command(command_class(**arg_dict))
    else:
        insert_index = select_command("Select the position to insert the new command:")
        if insert_index is None:
            return
        seq.add_command(command_class(**arg_dict), insert_index)


def remove_commands():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands.")
        return

    del_indices = select_multiple_commands(
        "Select the command(s) you would like to remove:"
    )
    if len(del_indices) == 0:
        print(Fore.RED + "No commands were deleted (Select commands with Space Bar)")
        return

    # Must sort in descending order otherwise removing earlier commands will shift later commands
    del_indices.sort(reverse=True)
    response = questionary.confirm(
        "Are you sure you want to delete the command(s)?", default=False
    ).ask()
    if response:
        for del_index in del_indices:
            seq.remove_command(del_index)
            print(Fore.GREEN + "Successfully removed command(s)")
    else:
        print(Fore.RED + "No commands were deleted")
        return


def move_command():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands.")
        return
    if len(seq.command_list) == 1:
        print(Fore.RED + "There is currently only one command.")
        return

    old_index = select_command("Select the command you would like to move:")
    if old_index is None:
        return
    new_index = select_command("Select where to move the command to:")
    if new_index is None:
        return
    seq.move_command_by_index(old_index, new_index)


def add_loop():
    if seq.count_loop_commands() > 0:
        print(
            Fore.RED + "Recipe already has loop commands. Remove them and re-add them."
        )
        return
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands.")
        return

    loop_indices = select_multiple_commands(
        "Select the FIRST and LAST commands of the loop section:",
        validator_func=valid_loop_count,
    )

    if len(loop_indices) == 0:
        print(Fore.RED + "Loop was NOT added to the recipe.")
        return

    loop_indices.sort()
    loop_start_index = loop_indices[0]
    loop_end_index = loop_indices[1] + 1
    seq.add_loop_end(loop_end_index)
    seq.add_loop_start(loop_start_index)
    print(Fore.GREEN + "Loop has been added to recipe!")


def remove_loops():
    response = questionary.confirm(
        "Are you sure you want to delete all loop commands?", default=False
    ).ask()
    if response:
        loop_command_count = seq.count_loop_commands()
        seq.remove_all_loop_commands()
        print(
            Fore.GREEN
            + "Removed "
            + str(loop_command_count)
            + " loop commands. If these loop commands were erroneously part of an iteration then you should fix your recipe."
        )
    else:
        print(Fore.RED + "No loop commands were deleted")
        return


def get_all_command_classes(command_dir: str):
    # initialize lists
    module_names = []
    cls_list = []
    cls_name_list = []
    cls_dict = {}

    # check if each file is a "regular file" with extension ".py" and neglecting the "__init__.py" file
    # then add to module_names str list
    for file in listdir(command_dir):
        if (
            isfile(join(command_dir, file))
            and file != "__init__.py"
            and file.split(".")[1] == "py"
        ):
            # get rid of the file extension and replace / with .
            module_name = join(command_dir, file).split(".")[0].replace("/", ".")
            module_names.append(module_name)

    # import each module
    # for each module get each class, if the class is not the base class Command and is not already on our list, then add it to our list
    for module_name in module_names:
        module = importlib.import_module(module_name)
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, Command) and cls is not Command and cls not in cls_list:
                if not "ParentCommand" in name:
                    cls_list.append(cls)
                    cls_name_list.append(name)
                    cls_dict[name] = cls
    return cls_dict


def get_all_commands_classes_for_receiver(command_dir: str, receiver_class):
    cls_dict = get_all_command_classes(command_dir)

    valid_dict = {}
    for name, cls in cls_dict.items():
        if cls.receiver_cls == receiver_class:
            valid_dict[name] = cls
    return valid_dict


##################################################
# Iteration Menu
##################################################
def iteration_menu():
    while True:
        if isinstance(seq.num_iterations, str):
            # Because I want the quotes to appear if it is a string
            num_iter_str = "'" + seq.num_iterations + "'"
        else:
            num_iter_str = str(seq.num_iterations)

        command_menu_prompt = "Command Iteration Menu - Choose an option:"
        command_menu_options = {
            "Display a Command's Iterations": display_command_iterations,
            "Add Command Iteration": add_command_iteration,
            "Remove Command Iteration(s)": remove_command_iterations,
            "Move Command Iteration": move_command_iteration,
            "Set Number of Loop Iterations (currently="
            + num_iter_str
            + ")": set_num_iterations,
            "Back to Main Menu": main_menu,
        }
        prompt = questionary.select(
            command_menu_prompt,
            choices=list(command_menu_options.keys()),
            style=custom_style,
        )
        response = prompt.ask()
        response_function = command_menu_options[response]
        response_function()


def add_command_iteration():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands.")
        return

    command_index = select_command("Select the command to add an iteration for:")
    if command_index is None:
        return

    for iteration in seq.command_list[command_index]:
        if isinstance(iteration, LoopStartCommand) or isinstance(
            iteration, LoopEndCommand
        ):
            print(Fore.RED + "Cannot add iteration to a Loop Start/End Command")
            return

    first_command_iteration = seq.command_list[command_index][0]
    device = first_command_iteration._receiver
    command_class = first_command_iteration.__class__

    arg_dict = prompt_signature_args(command_class.__init__, ["receiver"])
    arg_dict["receiver"] = device
    arg_dict["delay"] = prompt_delay()

    append_insert = questionary.select(
        "Append this command to the iteration list or insert at a specific position?",
        choices=["Append", "Insert"],
        style=custom_style,
    ).ask()
    if append_insert == "Append":
        seq.add_command_iteration(command_class(**arg_dict), index=command_index)
    else:
        insert_index = select_command_iteration(
            command_index, "Select the position to insert the new command iteration:"
        )
        if insert_index is None:
            return
        seq.add_command_iteration(
            command_class(**arg_dict), index=command_index, iteration=insert_index
        )


def remove_command_iterations():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands.")
        return

    command_index = select_command("Select the command to add an iteration for:")
    if command_index is None:
        return

    if len(seq.command_list[command_index]) == 1:
        print(
            Fore.RED
            + "Selected command only has 1 command iteration. To change it, insert a new command or command iteration in its place then delete the old one."
        )
        return

    del_indices = select_multiple_command_iterations(
        command_index, "Select the command iterations(s) you would like to remove:"
    )
    if len(del_indices) == 0:
        print(
            Fore.RED
            + "No command iterations were deleted (Select command iterations with Space Bar)"
        )
        return

    if len(del_indices) == len(seq.command_list[command_index]):
        print(Fore.RED + "There must be at least one iteration remaining")
        return

    # Must sort in descending order otherwise removing earlier commands will shift later commands
    del_indices.sort(reverse=True)
    response = questionary.confirm(
        "Are you sure you want to delete the command iterations(s)?", default=False
    ).ask()
    if response:
        for del_index in del_indices:
            seq.remove_command_iteration(command_index, del_index)
            print(Fore.GREEN + "Successfully removed command iteration(s)")
    else:
        print(Fore.RED + "No command iterations were deleted")
        return


def move_command_iteration():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands.")
        return

    command_index = select_command("Select the command to move iterations for:")
    if command_index is None:
        return

    if len(seq.command_list[command_index]) == 1:
        print(Fore.RED + "There is currently only one command iteration.")
        return

    old_index = select_command_iteration(
        command_index, "Select the command iteration you would like to move:"
    )
    if old_index is None:
        return
    new_index = select_command_iteration(
        command_index, "Select where to move the command iteration to:"
    )
    if new_index is None:
        return
    seq.move_command_iteration_by_index(command_index, old_index, new_index)


def set_num_iterations():
    print("")
    is_valid = False
    while not is_valid:
        print(
            Fore.WHITE
            + "The current number of iterations is: "
            + Fore.YELLOW
            + str(seq.num_iterations)
        )
        print("")
        response = questionary.text(
            "Enter the number of iterations to perform (minimum = 1, automatic = 'ALL'):",
            default="ALL",
        ).ask()
        if response == "ALL":
            num_iterations = "ALL"
            is_valid = True
        else:
            try:
                num_iterations = int(response)
                if num_iterations >= 1:
                    is_valid = True
                else:
                    print(
                        Fore.RED
                        + "Invalid value for num iterations. It must be an integer >= 1 or the string 'ALL'."
                    )
            except ValueError:
                print(
                    Fore.RED
                    + "Invalid value for num iterations. It must be an integer >= 1 or the string 'ALL'."
                )
    seq.num_iterations = num_iterations


##################################################
# Execute Recipe
##################################################
def execute_recipe():
    if len(seq.command_list) == 0:
        print(Fore.RED + "There are currently no commands.")
        return

    log_options = [
        "Log with default timestamped filename",
        "Log with specified filename",
        "No logging",
    ]
    response = questionary.select(
        "Select logging option:",
        choices=log_options,
        default=log_options[0],
        style=custom_style,
    ).ask()

    if response == log_options[0]:
        log_to_file = True
        log_filename = None
        print(Fore.GREEN + "Log filename will be displayed before and after execution!")
    elif response == log_options[1]:
        log_to_file = True
        log_filename = questionary.path(
            "Enter log file to create:",
            default=log_directory,
            validate=lambda file: valid_log_file(file, log_directory),
            style=custom_style,
        ).ask()
        print(Fore.GREEN + "Log messages will be saved to '" + log_filename + "'!")
    else:
        log_to_file = False
        log_filename = None
        print(Fore.YELLOW + "Messages will not be logged to file!")

    alert_slack = questionary.confirm(
        "Do you want to alert Slack if the recipe fails?", default=True
    ).ask()
    response = questionary.confirm("Are you ready to execute the recipe?").ask()
    if response:
        invoker = CommandInvoker(seq, log_to_file, log_filename, alert_slack)
        invocation_successful = invoker.invoke_commands()
        if invocation_successful:
            print(
                Fore.CYAN
                + "Recipe execution complete."
                + Fore.GREEN
                + " Execution was successful."
            )
        else:
            print(
                Fore.CYAN
                + "Recipe execution complete."
                + Fore.RED
                + " Execution encountered errors."
            )
        print("")


##################################################
# Execute Manual Commands
##################################################
def execute_manual():
    global seq
    if len(seq.device_list) == 0:
        print(
            Fore.RED
            + "There are currently no devices. Add a device to execute commands for it."
        )
        return

    # Warning! Manual command execution can alter the state of your devices which may or may not be desired!
    # For example, it can cause a device to have its is_initialized flag set to True, which can be dumped to a .yaml file
    # This means loading the "recipe" later will start with an initialized device even if it may not be initialized in reality
    # An option is to make a deepcopy of the device objects and execute commands on them
    # However, changing the state of the device may actually be desired!
    # For example, you may actually want to manually get the device to a certain state before executing the full recipe
    # Therefore, manual commands executed here have the option to operate on the same device/receiver objects as the recipe using a shallow copy
    # So use carefully! Try not to save to .yaml file after executing commands manually, instead reload this program to make changes then save

    # response = questionary.confirm("WARNING! Executing commands manually can alter the state of your devices which may be undesirable. Continue?", default=False, style=questionary.Style([("question", "fg:#ff0000"),])).ask()
    print(
        Fore.RED
        + "WARNING! Executing commands manually can alter the state of your devices which may be undesirable."
    )
    print(
        Fore.RED
        + "*BUG - Performing a deepcopy after previously performing a shallow copy results in an error."
    )
    # response = questionary.confirm("Do you want to preserve the state of the devices after execution? (Recommend No!)", default=False, style=questionary.Style([("question", "fg:#ff0000"),])).ask())
    copy_options = [
        "No, DO NOT preserve the state of the devices (Recommended, performs a deepcopy and creates new device objects)",
        "Yes, preserve the state of the devices (performs a shallow copy and references the original device objects)",
    ]
    prompt = questionary.select(
        "Do you want to preserve the state of the devices after execution?",
        choices=copy_options,
        default=copy_options[0],
        style=custom_style,
    )
    response = prompt.ask()

    if response == copy_options[0]:
        # Do not preserve the device state
        seq_manual = copy.deepcopy(seq)
    else:
        # Preserve the device state
        seq_manual = copy.copy(seq)

    seq_manual.command_list = []
    seq_manual.num_iterations = 1

    # Enter the manual execution loop, Choose device
    while True:
        seq_manual.command_list = []
        # copied from add_command (refactor this)
        device_index = select_device("Choose a device to execute commands for:")
        if device_index is None:
            break

        device = seq_manual.device_list[device_index]

        valid_command_dict = get_all_commands_classes_for_receiver(
            command_directory, device.__class__
        )
        valid_command_names_desc = []
        for name, cls in valid_command_dict.items():
            valid_command_names_desc.append(
                "{:30.30s}".format(name) + "- " + cls.__doc__
            )
        valid_command_names_desc.append("Go back")

        # Choose command loop
        while True:
            response = questionary.select(
                "Choose the command to add:",
                choices=valid_command_names_desc,
                style=custom_style,
            ).ask()
            if response == "Go back":
                break
            command_class_name = response.split(" ")[0]
            command_class = valid_command_dict[command_class_name]

            arg_dict = prompt_signature_args(command_class.__init__, ["receiver"])
            arg_dict["receiver"] = device
            arg_dict["delay"] = prompt_delay()

            response = questionary.confirm(
                "Are you sure you want to execute this command?",
                default=True,
                style=questionary.Style(
                    [
                        ("question", "fg:#ff0000"),
                    ]
                ),
            ).ask()
            if not response:
                break

            seq_manual.command_list = []
            seq_manual.add_command(command_class(**arg_dict))
            invoker_manual = CommandInvoker(
                seq_manual, log_to_file=False, log_filename=None, alert_slack=False
            )
            invocation_successful = invoker_manual.invoke_commands()

            if invocation_successful:
                print(
                    Fore.CYAN
                    + "Manual command execution complete."
                    + Fore.GREEN
                    + " Execution was successful."
                )
            else:
                print(
                    Fore.CYAN
                    + "Manual command execution complete."
                    + Fore.RED
                    + " Execution encountered errors."
                )
            print("")


##################################################
# Print Help
##################################################
def print_help():
    print("")
    print(Fore.GREEN + "=" * 10 + " How to use this tool? " + "=" * 140)
    # print(rainbow('#?')*1 + Fore.CYAN + "  How to use this tool  " + rainbow('#?')*14)
    print("")
    print(
        Fore.WHITE
        + " 1) Add devices that will be needed for the recipe. You will be prompted for parameters (e.g. COM port, timeout, motor numbers, etc.)"
    )
    print(
        " 2) Add commands for any device that has been added. You will be prompted for parameters if any. (e.g. temperature, speed, position, etc.)"
    )
    print(
        " 3) After adding commands, you can designate a subsection of the recipe as a looped section using 'Add Loop'. The looped section will execute a specified number of iterations."
    )
    print(
        " 4) For each command, you can add additional 'command iterations' which are additional commands that correspond to each loop iteration."
    )
    print(
        "         (If there are more loop iterations (at least 1) than command's 'command iterations', the latest command iteration will be used.)"
    )
    print(
        " 5) You can set the integer number of loop iterations in the command iteration menu. A string value of 'ALL' will automatically determine the largest command iteration length and use that."
    )
    print(" 6) Frequently save you recipe to a .yaml file so it can be loaded later")
    print(
        " 7) When ready to execute the recipe you will be prompted for logging options, slack alerts, and a final confirmation before execution."
    )
    print(
        " 8) During execution the status will be updated live and logged to the screen and log file. After completion you will be returned to the main menu."
    )
    print("")
    # print(rainbow('#?')*17)
    print(Fore.GREEN + "=" * 173)
    # print(rainbow("#")*10)
    # print(rainbow("?")*10)
    # print(rainbow_bg()*10)
    print("")


##################################################
# Quit
##################################################
def quit_program():
    print(Fore.RED + "User quit program")
    sys.exit()


##################################################
# Useful Functions
##################################################
def select_device(prompt_message, allow_backout=True):
    device_names_classes = (
        seq.get_device_names_classes()
    )  # [name, class name] of every device
    display_device_menu_options = []
    for name_class in device_names_classes:
        display_device_menu_options.append(
            "Name: {:20.20s} Class: {}".format(name_class[0], name_class[1])
        )
    if allow_backout:
        display_device_menu_options.append("Go back")
    prompt = questionary.select(
        prompt_message, choices=display_device_menu_options, style=custom_style
    )
    response = prompt.ask()
    if response == "Go back":
        response = None
    else:
        response = display_device_menu_options.index(response)
    return response  # index of the device


def select_command(prompt_message, allow_backout=True):
    command_names = seq.get_command_names()
    # Any command with additional iterations is marked with *
    for ndx, name in enumerate(command_names):
        if "IterIndex" in name:
            command_names[ndx - 1] = "*" + command_names[ndx - 1]
    # Delete the iterations from the list
    for ndx, name in enumerate(command_names):
        while "IterIndex" in command_names[ndx]:
            del command_names[ndx]
    # Format the string with spaces
    for ndx, name in enumerate(command_names):
        name_parts = name.strip().split(" ")
        command_names[ndx] = "{:4s}".format(str(ndx)) + "{:30s}".format(
            name_parts.pop(0)
        )
        if len(name_parts) > 0:
            for param in name_parts:
                command_names[ndx] += " " + param
    if allow_backout:
        command_names.append("Go back")
    prompt = questionary.select(
        prompt_message, choices=command_names, style=custom_style
    )
    response = prompt.ask()
    if response == "Go back":
        response = None
    else:
        response = command_names.index(response)
    return response  # index of the command


def select_multiple_commands(prompt_message, validator_func=None):
    command_names = seq.get_command_names()
    # Any command with additional iterations is marked with *
    for ndx, name in enumerate(command_names):
        if "IterIndex" in name:
            command_names[ndx - 1] = "*" + command_names[ndx - 1]
    # Delete the iterations from the list
    for ndx, name in enumerate(command_names):
        while "IterIndex" in command_names[ndx]:
            del command_names[ndx]
    # Format the string with spaces
    for ndx, name in enumerate(command_names):
        name_parts = name.strip().split(" ")
        command_names[ndx] = "{:4s}".format(str(ndx)) + "{:30s}".format(
            name_parts.pop(0)
        )
        if len(name_parts) > 0:
            for param in name_parts:
                command_names[ndx] += " " + param
    if validator_func is None:
        prompt = questionary.checkbox(
            prompt_message, choices=command_names, style=custom_style
        )
    else:
        prompt = questionary.checkbox(
            prompt_message,
            choices=command_names,
            validate=lambda resp: validator_func(resp),
            style=custom_style,
        )
    response_list = prompt.ask()
    index_list = []
    for response in response_list:
        index_list.append(command_names.index(response))
    return index_list


def select_command_iteration(command_index, prompt_message, allow_backout=True):
    iteration_names = []
    for iteration in seq.command_list[command_index]:
        iteration_names.append(iteration.name)

    for ndx, name in enumerate(iteration_names):
        name_parts = name.strip().split(" ")
        iteration_names[ndx] = "{:4s}".format(str(ndx)) + "{:30s}".format(
            name_parts.pop(0)
        )
        if len(name_parts) > 0:
            for param in name_parts:
                iteration_names[ndx] += " " + param

    if allow_backout:
        iteration_names.append("Go back")
    prompt = questionary.select(
        prompt_message, choices=iteration_names, style=custom_style
    )
    response = prompt.ask()
    if response == "Go back":
        response = None
    else:
        response = iteration_names.index(response)
    return response  # index of the command iteration


def select_multiple_command_iterations(command_index, prompt_message):
    iteration_names = []
    for iteration in seq.command_list[command_index]:
        iteration_names.append(iteration.name)

    for ndx, name in enumerate(iteration_names):
        name_parts = name.strip().split(" ")
        iteration_names[ndx] = "{:4s}".format(str(ndx)) + "{:30s}".format(
            name_parts.pop(0)
        )
        if len(name_parts) > 0:
            for param in name_parts:
                iteration_names[ndx] += " " + param

    prompt = questionary.checkbox(
        prompt_message, choices=iteration_names, style=custom_style
    )
    response_list = prompt.ask()
    index_list = []
    for response in response_list:
        index_list.append(iteration_names.index(response))
    return index_list


def prompt_signature_args(func, ignored_args):
    # ignored args, list of strings for arg names
    # returns dictionary of args
    sig = inspect.signature(func)
    arg_dict = {}
    ignored_args.extend(["self", "kwargs", "args"])

    for param in sig.parameters.values():
        if not param.name in ignored_args:
            print_eval_warning()
            if param.default == inspect._empty:
                default = "N/A"
            else:
                default = str(param.default)
            print(
                Fore.WHITE
                + "Parameter: "
                + Fore.GREEN
                + param.name
                + Fore.WHITE
                + "  type: "
                + Fore.YELLOW
                + str(param.annotation)
                + Fore.WHITE
                + "  default: "
                + Fore.YELLOW
                + default
            )

            if default == "N/A":
                response = questionary.text("Enter value for the parameter").ask()
            else:
                response = questionary.text(
                    "Enter value for the parameter", default=default
                ).ask()

            arg_dict[param.name] = eval(response)
    return arg_dict


def prompt_delay():
    # print(Fore.WHITE + "Parameter: " + Fore.GREEN + "delay" + Fore.WHITE + "  type: " + Fore.YELLOW + "float" + Fore.WHITE + "  default: " + Fore.YELLOW + "0.0")
    is_valid = False
    while not is_valid:
        response = questionary.text(
            "Enter delay (in seconds) before this command executes. (0.0 = no delay, P = Pause & wait for ENTER before execute):",
            default="0.0",
        ).ask()
        if response == "P" or response == "PAUSE":
            delay = "PAUSE"
            is_valid = True
        else:
            try:
                delay = float(response)
                if delay >= 0.0:
                    is_valid = True
                else:
                    print(
                        Fore.RED
                        + "Invalid value for delay. It must be an number >= 0.0 or the string 'P' or 'PAUSE'."
                    )
            except ValueError:
                print(
                    Fore.RED
                    + "Invalid value for delay. It must be an number >= 0.0 or the string 'P' or 'PAUSE'."
                )
    return delay


def print_eval_warning():
    print(Fore.RED + "Your response will be evaluated directly with eval()!")
    print(
        Fore.RED
        + "Examples: string = 'COM9', integer = 5, float = 5.0, list of ints = [1, 2, 3], tuple of ints = (1, 2, 3)"
    )


def print_intro():
    print(Fore.GREEN + Style.BRIGHT + "=" * 50)
    print(" " * 15 + "Command Recipe Tool")
    print(" " * 13 + "8/12/2021 - Justin Kwok")
    print("=" * 50)
    print("")


def rainbow(char):
    string = (
        Fore.RED
        + char
        + Fore.YELLOW
        + char
        + Fore.GREEN
        + char
        + Fore.CYAN
        + char
        + Fore.BLUE
        + char
        + Fore.MAGENTA
        + char
    )
    return string


def rainbow_bg():
    char = " "
    string = (
        Back.RED
        + char
        + Back.YELLOW
        + char
        + Back.GREEN
        + char
        + Back.CYAN
        + char
        + Back.BLUE
        + char
        + Back.MAGENTA
        + char
    )
    return string


##################################################
# Questionary validator functions
##################################################
def valid_yml(file):
    if file.lower() == "quit":
        return True
    if not isfile(file) or (
        file.split(".")[-1] != "yml" and file.split(".")[-1] != "yaml"
    ):
        return "Enter a valid yml/yaml file"
    else:
        return True


def valid_loop_count(response_list):
    if len(response_list) == 0 or len(response_list) == 2:
        return True
    else:
        return "You must select 2 options only or select none to exit"


def valid_save_file(file, save_directory):
    if file.lower() == "quit":
        return True
    if not save_directory in file:
        return "You must save in the directory: " + save_directory
    if not ".yaml" in file:
        return "File must have a '.yaml' extension"
    else:
        return True


def valid_log_file(file, log_directory):
    if not log_directory in file:
        return "You must save log in the directory: " + log_directory
    if not ".log" in file:
        return "File must have a '.log' extension"
    if isfile(file):
        return "You must create a new log file"
    else:
        return True


if __name__ == "__main__":
    main()

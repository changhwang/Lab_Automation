import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from skopt import Optimizer
from skopt.plots import plot_convergence, plot_gaussian_process
import pandas as pd

from command_sequence import CommandSequence
from command_invoker import CommandInvoker

from devices.dummy_heater import DummyHeater
from devices.dummy_motor import DummyMotor
from devices.dummy_meter import DummyMeter
from commands.dummy_heater_commands import *
from commands.dummy_motor_commands import *
from commands.dummy_meter_commands import *

def main():
    # This is only for creating a .yaml recipe file. You can create and save the recipe in a different script.
    # Or if you already have a .yaml recipe then you can just start with that instead of creating it here
    create_recipe()

    # Initialize bayesian optimizer
    opt = Optimizer([(25.0,100.0),(5.0,50.0)], base_estimator='GP', acq_func='gp_hedge', n_initial_points=10, initial_point_generator='grid', random_state=None)

    max_iter = 30
    for i in range(max_iter):
        meter_file = "myexp_run" + str(i)
        
        # Get conditions to sample
        next_x = opt.ask()
        
        # Run the experiment at the given conditions
        run_experiment(next_x, meter_file)

        # Process the raw data
        data_file = 'data/dummy_meter/' + meter_file + '.csv'
        fval = process_data(data_file)

        # Update the optimizer with objective function value
        result = opt.tell(next_x, fval)

    # Printing results
    print("========== RESULT ==========")
    print(result)
    print()
    print("Lowest minimum of " + str(result.fun) + " at " + str(result.x))
    fig2 = plt.figure()
    plot_convergence(result)
    plt.show()
    input("\nPress Enter to quit")

def create_recipe():
    # Generate coefficients only for emulating the objective function
    n_fourier = 3
    a1 = np.random.uniform(-1, 1, size=(n_fourier,1))
    b1 = np.random.uniform(-1, 1, size=(n_fourier,1))
    a2 = np.random.uniform(-1, 1, size=(n_fourier,1))
    b2 = np.random.uniform(-1, 1, size=(n_fourier,1))
    noise_width = 0.1

    ##### Start of actual recipe creation
    # Create new command sequence
    seq = CommandSequence()

    # Create devices
    heater = DummyHeater('heater', heat_rate=40.0)
    motor = DummyMotor('motor')
    meter = DummyMeter('meter', heater, motor, a1, b1, a2, b2, noise_width)

    # Add devices to sequence
    seq.add_device(heater)
    seq.add_device(motor)
    seq.add_device(meter)

    # Add commands to sequence to form experimental procedure
    seq.add_command(DummyHeaterInitialize(heater))
    seq.add_command(DummyMotorInitialize(motor))
    seq.add_command(DummyMeterInitialize(meter))

    seq.add_command(DummyMotorMoveSpeedAbsolute(motor, 50.0, 5.0)) # Pretend to move printer to start position
    seq.add_command(DummyHeaterSetTemp(heater, 25.0)) # index 4, Set print temperature
    seq.add_command(DummyMotorSetSpeed(motor, 5.0)) # index 5, Set print speed
    seq.add_command(DummyMotorMoveRelative(motor, distance=5.0)) # Pretend to print material
    seq.add_command(DummyMotorMoveRelative(motor, distance=-5.0)) # Move motor back to original position
    # Various sample manipulation and processing commands here
    # Then measure material
    seq.add_command(DummyMeterMeasure(meter, filename=None)) # index 8, Measure the material and store data in file
    # Other measurement, sample manipulation, and processing commands here

    # Optionally deinitialize devices, but may be unnecessary
    seq.add_command(DummyHeaterDeinitialize(heater))
    seq.add_command(DummyMotorDeinitialize(motor))
    seq.add_command(DummyMeterDeinitialize(meter))

    seq.num_iterations = 1

    # Save recipe to .yaml file
    seq.print_command_names()
    recipe_file = 'recipes/example6.yaml'
    seq.save_to_yaml(recipe_file)
    ##### End of recipe creation

    ##### Plot the objective function without noise for our reference (Can't do this for real experiements)   
    n_pts = 200
    x1 = np.linspace(meter.x1_range[0], meter.x1_range[1], n_pts).reshape(-1, 1)
    x2 = np.linspace(meter.x2_range[0], meter.x2_range[1], n_pts).reshape(-1, 1)
    Y = np.zeros((n_pts, n_pts))

    for i in range(len(x1)):
        for j in range(len(x2)):
            Y[j,i] = meter.fourier2d([x1[i], x2[j]], meter.x1_range, meter.x2_range, a1, b1, a2, b2, noise_width=0.0)

    X1, X2 = np.meshgrid(x1, x2)
    fig1 = plt.figure()
    ax = fig1.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X1, X2, Y, cmap=cm.coolwarm)

    ax.set_xlabel('Temperature')
    ax.set_ylabel('Speed')
    ax.set_zlabel('Data')
    fig1.colorbar(surf, shrink=0.5, aspect=5)
    plt.ion()
    plt.show() 


def run_experiment(params, meter_file):
    # Alternatively you can simply create the recipe, devices, and commands each time for better readability
    # But you lose the ability to save the device object states from run to run if that is desired
    # And you may want to start with a pre-existing recipe .yaml file anyways

    # Load the recipe
    recipe_file = 'recipes/example6.yaml'
    seq = CommandSequence()
    seq.load_from_yaml(recipe_file)

    # Get tunable parameters from argument
    temperature = params[0]
    speed = params[1]

    # Edit the commands
    # (Alternatively you could have left out these commands when originally created and inserted them in here (insert them in reverse order to avoid index shifting))
    seq.add_command_iteration(DummyHeaterSetTemp(seq.device_by_name['heater'], temperature), index=4, iteration=0)
    seq.remove_command_iteration(index=4, iteration=1)

    seq.add_command_iteration(DummyMotorSetSpeed(seq.device_by_name['motor'], speed), index=5, iteration=0)
    seq.remove_command_iteration(index=5, iteration=1)

    seq.add_command_iteration(DummyMeterMeasure(seq.device_by_name['meter'], meter_file), index=8, iteration=0)
    seq.remove_command_iteration(index=8, iteration=1)

    invoker = CommandInvoker(seq, log_to_file=True, log_filename='logs/example6.log', alert_slack=False)
    invoker.invoke_commands()

    # If you wish to save the state of your device objects then overwrite your save file
    seq.save_to_yaml(recipe_file)

def process_data(data_file):
    dataframe = pd.read_csv(data_file)
    raw_data = dataframe.iloc[0]['Data']
    # Process your data here
    processed_data = raw_data
    return processed_data

if __name__ == "__main__":
    main()
    


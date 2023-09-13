import json
import random
import matplotlib.pyplot as plt

import gcc_phat, gui, sig_gen, signal_procesing, triangulation

def main():
    with open("Simulation/sim_config.json", "r") as read_file:
        config = json.load(read_file)

    # populate global points randomly
    if config["points"]["random"]:
        populate_random_points(config["points"], 0.8, 0.5)

    # loop over specified test parameters
    for test in config["tests"]:

        for key in test:
            populate_test_from_global(config, test, key)

        for point in test["points"]["points"]:
            


            signals = []

            for mic_loc in test["mics"]["mics"]:
                signals.append(sig_gen.generate_signal(point, mic_loc, test["frequency"]["value"], amplitude=6))
            
            tdoas = []

            for i in range(len(signals)-1):
                tau, cc = gcc_phat.gcc_phat(signals[i+1], signals[0], 44100)
                tdoas.append(tau)

            print(tdoas)

            





        

# adds a random point to a list
def add_point(points, max_x, max_y):
    points.append([random.uniform(0, max_x), random.uniform(0, max_y)])


# used to populate an array of points randomly, up to the specified max number of points
def populate_random_points(points_dict, max_x, max_y):
    for i in range(points_dict["number"] - len(points_dict["points"])):
        add_point(points_dict["points"], max_x, max_y)

def populate_test_from_global(config, test, key):
    if test[key]["global"]:
        test[key] = config[key]

if __name__ == "__main__":
    main()
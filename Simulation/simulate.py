import json
import random


def main():
    with open("Simulation/sim_config.json", "r") as read_file:
        config = json.load(read_file)

    # populate global points randomly
    if config["points"]["random"]:
        populate_random_points(config["points"], 0.8, 0.5)

    # loop over specified test parameters
    for test in config["tests"]:

        #import global frequency
        if test["frequency"]["global"]:
            test["frequency"] = config["frequency"]
        
        # import global points array
        if test["points"]["global"]:
            test["points"] = config["points"]
        elif test["points"]["random"]:
            populate_random_points(test["points"], 0.8, 0.5)

        # import global mic positions
        if test["mics"]["global"]:
            test["mics"] = config["mics"]

    
    with open("config_edit_test.json", "w") as write_file:
        json.dump(config, write_file)


        

# adds a random point to a list
def add_point(points, max_x, max_y):
    points.append([random.uniform(0, max_x), random.uniform(0, max_y)])


# used to populate an array of points randomly, up to the specified max number of points
def populate_random_points(points_dict, max_x, max_y):
    for i in range(points_dict["number"] - len(points_dict["points"])):
        add_point(points_dict["points"], max_x, max_y)

if __name__ == "__main__":
    main()
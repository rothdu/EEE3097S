import json
import random
import matplotlib.pyplot as plt
import scipy.constants as constant
import gcc_phat, gui, sig_gen, signal_procesing, triangulation
import pyroomacoustics

def main():
    with open("Simulation/sim_config.json", "r") as read_file:
        config = json.load(read_file)

    # populate global points randomly
    if config["points"]["random"]:
        populate_random_points(config["points"], 0.8, 0.5)

    # loop over specified test parameters
    for test in config["tests"]:

        # Populate global config parameters for the specific test
        for key in test:
            populate_test_from_global(config, test, key)


        # loop over the set of test points
        for point in test["points"]["points"]:
            

            # initialise list to store the signals
            signals = []

            # generate unique signal for each mic
            for mic_loc in test["mics"]["mics"]:
                signals.append(sig_gen.generate_signal(point, mic_loc, test["frequency"]["value"], amplitude=6, sample_length=1))
            
            # convert to an equivalent wav file
            for signal in signals:
                signal = sig_gen.signal_to_16_bit(signal)

            
            # initialise list to store tdoas
            tdoas = []

            # use gcc-phat on pairs of signals, using first signal as reference
            for i in range(1, len(signals)):
                #tau = gcc_phat.gcc_phat_2(signals[i], signals[0], fs=44100)
                tau = pyroomacoustics.experimental.localization.tdoa(signals[0], signals[i])
                tdoas.append(tau)


            # convert tdoas to distances for triangulation
            distancesize = lambda x: x* constant.speed_of_sound
            dists = list(map(distancesize, tdoas))

            # for debugging
            print(point)
            print(tdoas)


            mics = test["mics"]["mics"]

            # pick out parameters for triangulation
            tri_param = [mics[0][0], mics[0][1], mics[1][0], mics[1][1], dists[0], 
                         mics[2][0], mics[2][1], dists[1], mics[3][0], mics[3][1], dists[2]]
            tri_mesh = [0, 0.8, 0.8/100, 0, 0.5, 0.5/100]

            # perform triangulation
            xe, ye, x, y, h1, h2, h3 = triangulation.triangulate(tri_param,tri_mesh)
            xs, ys = point[0], point[1]
    
            # plot triangulation stuff
            plt.contour(x,y,h1,[0])
            plt.contour(x,y,h2,[0])
            plt.contour(x,y,h3,[0])
            plt.plot(xs,ys,'co',markersize=10)
            plt.plot(xe,ye,'r.',markersize=10)
            plt.show()

            

            





        

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
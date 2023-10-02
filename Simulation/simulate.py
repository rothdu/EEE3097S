import json
import random
import scipy.constants as constant
import gcc_phat
import gui
import signal_procesing
import triangulation2
import wav_signal
import time

def main():
    start_time = time.time()
    with open("Simulation/sim_config.json", "r") as read_file:
        config = json.load(read_file)

    # populate global points randomly
    if config["points"]["random"]:
        populate_random_points(config["points"], 0.8, 0.5)

    # tests(config) # no noise tests
    print("Starting Gaussian Noise Test\n")
    tests(config, "g")

    print("Starting Impulse Noise Test\n")
    tests(config, "i")

    print("Starting Pink Noise Test\n")
    tests(config, "p")

    print("Starting No Noise Test\n")
    tests(config)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed time: ", elapsed_time) 


# noisetype can be any combination of "g", "p", and "i", e.g., "gpi", "ip", "g", etc.
# the output signal for the tests will use all of the specified noise types
def tests(config, noisetype="none"):
    # LOAD SOUND FILE
    sample_rate, refsig = wav_signal.load_signal("Simulation/snap.wav")

    # debug
    count_mic_conf = 1

    # loop over specified test parameters
    for test in config["tests"]:

        # Populate global config parameters for the specific test
        for key in test:
            populate_test_from_global(config, test, key)

        # initialise resultantant arrays
        x_est = []
        y_est = []
        all_est_tdoas = []
        all_act_tdoas = []
        hyperbolas = []
        all_points = []

        noisy = False
    
        # loop over the set of test points
        for point in test["points"]["points"]:

            count = 0

            # debug
            # initialise list to store the signals
            signals = []

            # inititialize list to store the actual tdoas
            act_tdoas = []

            # generate unique signal for each mic
            for mic_loc in test["mics"]["mics"]:
                # generate signal and add to signals array as well as act_tdoa array
                # sig, tdoa = sig_gen.generate_signal(
                #     point, mic_loc, test["frequency"]["value"], amplitude=6)
                sig, t_d = wav_signal.gen_delay(
                    refsig, point, mic_loc, sample_rate, 4410)
                signals.append(sig)
                if count == 0:
                    ref_t_d = t_d
                    count += 1
                else:
                    act_tdoas.append(ref_t_d - t_d)

            # add signal noise
            if noisetype in "gpigippgipigigpipg" and noisetype != "":  # check for valid noise inputs
                noisy = True
                for signal_index in range(len(signals)):
                    signal = signals[signal_index]
                    signal_length = signal.shape[0] / 44100
                    signals[signal_index] = signal_procesing.add_noise(noisetype,
                                                                       signal, signal_length, 44100)

            # initialise list to store tdoas
            est_tdoas = []

            # use gcc-phat on pairs of signals, using first signal as reference
            for i in range(1, len(signals)):
                tau = gcc_phat.gcc_phat(
                    signals[0], signals[i], fs=sample_rate)
                est_tdoas.append(tau)

            # convert tdoas to distances for triangulation
            def distancesize(x): return x * constant.speed_of_sound
            dists = list(map(distancesize, est_tdoas))

            # for debugging
            # print(point)
            # print(act_tdoas)
            # print(est_tdoas)

            mics = test["mics"]["mics"]

            # pick out parameters for triangulation
            tri_param = [mics[0][0], mics[0][1], mics[1][0], mics[1][1], dists[0],
                         mics[2][0], mics[2][1], dists[1], mics[3][0], mics[3][1], dists[2]]
            tri_mesh = [0, 0.8, 0.8/100, 0, 0.5, 0.5/100]

            # perform triangulation
            xe, ye, x, y, h1, h2, h3 = triangulation2.triangulate(
                tri_param, tri_mesh)

            print("actual point = " + str(point))
            print("estimated tdoas = " + str(est_tdoas))
            print("actual tdoas = " + str(act_tdoas))
            print("estimated point = [" + str(xe) + "," + str(ye) + "]")
            print()

            # append resulting arrays
            x_est.append(xe)
            y_est.append(ye)
            # x_tri.append(x)
            # y_tri.append(y)
            all_est_tdoas.append(est_tdoas)
            all_act_tdoas.append(act_tdoas)
            hyperbolas.append([h1, h2, h3])
            all_points.append(point)

            # xs, ys = point[0], point[1]

            # plot triangulation stuff
            # plt.contour(x,y,h1,[0])
            # plt.contour(x,y,h2,[0])
            # plt.contour(x,y,h3,[0])
            # plt.plot(xs,ys,'co',markersize=10)
            # plt.plot(xe, ye, 'r.', markersize=10)
            # plt.show()

        print("Running GUI")

        # convert points to correct form for gui parameters
        x_test = [row[0] for row in all_points]
        y_test = [row[1] for row in all_points]

        # run the gui
        gui.run(test["frequency"]["value"], mics, x_test,
                y_test, x_est, y_est, 0.8, 0.5, 10, all_est_tdoas, all_act_tdoas, hyperbolas, x, y, noisy, noisetype)

        print("\nMic Configuration " + str(count_mic_conf) + " Tested\n")
        count_mic_conf += 1


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

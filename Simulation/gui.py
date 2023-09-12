import matplotlib.pyplot as plt
import math
from matplotlib.lines import Line2D
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
import pandas as pd
import os
import numpy as np

# define global variables
x_mics = None
y_mics = None

x_test = None
y_test = None
x_res = None
y_res = None

est_toa = None
act_toa = None

act_tri = None
est_tri = None

x_max = 0
y_max = 0
num_points = 0

parabolas = None

colours = None

test_dir = ""


# plot test points
def plot_test_points():
    global x_test, y_test, x_max, y_max, test_dir

    # Create a scatter plot
    plt.scatter(x_test, y_test, color='blue', marker='o')

    # Add labels and a title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Test Points on Grid')

    # Set limits for grid points
    plt.xlim(0, x_max) 
    plt.ylim(0, y_max)  

    # Save the figure as a JPEG file
    plt.savefig(test_dir + '/test_points.jpg',dpi=300)


# plot resultant points
def plot_result_points():
    global x_res, y_res, x_max, y_max, test_dir

    # Create a scatter plot
    plt.scatter(x_res, y_res, color='red', marker='o')

    # Add labels and a title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Result Points on Grid')

    # Set limits for grid points
    plt.xlim(0, x_max)  # Set x-axis limits from 0 to 6
    plt.ylim(0, y_max)  # Set y-axis limits from 0 to 12

    # Save the figure as a JPEG file
    plt.savefig(test_dir + '/result_points.jpg',dpi=300)


# plot test and resultant points
def plot_test_result_points():
    global x_res, y_res, x_test, y_test, x_max, y_max, test_dir, colours
    colours = plt.cm.viridis(np.linspace(0, 1, len(x_test)))

    # Create a scatter plot for each pair of test and resultant points
    for i in range(len(x_test)):
        plt.scatter(x_test[i], y_test[i], label=f'Test Point {i+1}', color=colours[i], marker='s', s=50)
        plt.scatter(x_res[i], y_res[i], label=f'Resultant Point {i+1}', color=colours[i], marker='o', s=50)

    legend_handles = [Line2D([0], [0], marker='s', color='w', label='Test Points', markersize=10, markerfacecolor='black'),Line2D([0], [0], marker='o', color='w', label='Resultant Points', markersize=10, markerfacecolor='black')]

    # Add labels and a legend
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Resultant & Test Points on Grid')
    plt.legend(handles=legend_handles)

    # Save the figure as a JPEG file
    plt.savefig(test_dir + '/test_result_points.jpg',dpi=300)

    


# plot test, result and parabolas for all array of test points
def plot_all_points():
    global x_test, y_test, x_res, y_res, x_mics, y_mics, x_max, y_max, parabolas, num_points

    # Create and save individual scatter plots
    for i, (x_t, y_t, x_r, y_r) in enumerate(zip(x_test,y_test,x_res,y_res)):
        plt.figure(figsize=(6, 4))
        plt.scatter(x_t, y_t, label=f'Test Point {i+1}', color=colours[i], marker='s', s=50)
        plt.scatter(x_r, y_r, label=f'Resultant Point {i+1}', color=colours[i], marker='o', s=50)
        for k in range(0,6,2):
             plt.plot(parabolas[i][k], parabolas[i][k+1], color='black')
        plt.xlim(0, x_max) 
        plt.ylim(0, y_max)  
        plt.grid(True)
        plt.title(f"Test Point {i+1} Results")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.grid(True)
        plt.savefig(test_dir + f"/Point_{i+1}.jpg")
        plt.close()

    # Create and display all scatter plots together in one figure using subplots
    fig, axs = plt.subplots(2, 5, figsize=(20, 8))

    for i, (x_t, y_t, x_r, y_r,ax) in enumerate(zip(x_test,y_test,x_res,y_res,axs.ravel())):
        ax.scatter(x_t, y_t, label=f'Test Point {i+1}', color=colours[i], marker='s', s=50)
        ax.scatter(x_r, y_r, label=f'Resultant Point {i+1}', color=colours[i], marker='o', s=50)
        for k in range(0,6,2):
             ax.plot(parabolas[i][k], parabolas[i][k+1], color='black')
        ax.set_title(f"Test Point {i+1}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend()
        ax.grid(True)


    plt.tight_layout()

    # Save the final subplotted scatter plots as an image
    plt.savefig(test_dir + "/subplotted_point_results.jpg", bbox_inches="tight")

# generate xlsx for time of arrival results
def ss_toa():
    global x_max, est_toa, act_toa, num_points
    
    points = np.linspace(1, num_points, num_points)
        
    data = {
        'Points' : points,
        'Mic 1 Actual ' : act_toa[0],
        'Mic 1 Estimated ' : est_toa[0],
        'Mic 2 Actual ' : act_toa[1],
        'Mic 2 Estimated ' : est_toa[1],
        'Mic 3 Actual ' : act_toa[2],
        'Mic 3 Estimated ' : est_toa[2],
        'Mic 4 Actual ' : act_toa[3],
        'Mic 4 Estimated ' : est_toa[3],
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Specify the Excel file name
    excel_file = test_dir + '/toa_results.xlsx'

    # Create a new Excel workbook
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Convert the DataFrame to rows and add them to the worksheet
    for row in dataframe_to_rows(df, index=False, header=True):
        worksheet.append(row)

    # Save the Excel file
    workbook.save(excel_file)

# generate xlsx for triangulation results
def ss_tri():
    global x_test, y_test, x_res, y_res
    
    points = np.linspace(1, num_points, num_points)
    
    act = []
    est = []
    dist_err = []
    for i in range(0, num_points):
        act.append('(' + str(x_test[i]) + ',' + str(y_test[i]) + ')')
        est.append('(' + str(x_res[i]) + ',' + str(y_res[i]) + ')')
        dist_err.append(math.sqrt((x_test[i] - x_res[i])**2 + (y_test[i] - y_res[i])**2))

    data = {
        'Points' : points,
        'Actual Co-Ord' : act,
        'Estimated Co-Ord' : est,
        'Error Distance ' : dist_err,
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Specify the Excel file name
    excel_file = test_dir + '/tri_results.xlsx'

    # Create a new Excel workbook
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Convert the DataFrame to rows and add them to the worksheet
    for row in dataframe_to_rows(df, index=False, header=True):
        worksheet.append(row)

    # Save the Excel file
    workbook.save(excel_file)

# generate xlsx for simulation input parameteres (frequency/microphone points)


# create directories for test results
def create_dir():
    global test_dir

    # create main test results directory if not already made
    test_dir = "Test_Results"
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    # create subsidiary test directory by finding the next available directory name
    found_dir = False
    count_dir = 1
    test_dir = test_dir + "/Test_Results"
    while found_dir == False:
        if not os.path.exists(test_dir + "_" + str(count_dir)):
            test_dir = test_dir + "_" + str(count_dir)
            os.mkdir(test_dir)
            found_dir = True
        count_dir += 1

# generate random parabola for testing
def rand_par(x_max):
    # Generate x values (e.g., from -5 to 5)
    x_values = np.linspace(0, x_max, 50)

    # Generate random coefficients for the parabola (a, b, c)
    a = np.random.uniform(-0.2, 0.2)
    b = np.random.uniform(-2.0, 2.0)
    c = np.random.uniform(0.0, 5.0)

    # Calculate y values using the parabola equation
    y_values = a * x_values**2 + b * x_values + c

    return x_values,y_values

# complete gui function for main sim program
def run(x_test_in,y_test_in,x_res_in,y_res_in,x_max_in,y_max_in,parabolas_in,num_points_in, est_toa_in, act_toa_in):
    # set all necessary global variables
    global x_test, y_test, x_res, y_res, x_mics, y_mics, x_max, y_max, parabolas, num_points, est_toa, act_toa    
    x_test = x_test_in
    y_test = y_test_in
    x_res = x_res_in
    y_res = y_res_in
    x_max = x_max_in
    y_max = y_max_in
    parabolas = parabolas_in
    num_points = num_points_in
    est_toa = est_toa_in
    act_toa = act_toa_in

    #create the relevant directories
    create_dir()

    # plot the result points
    plot_test_result_points()

    # plot test point, resultant point and parabolas for each test
    plot_all_points()

    # create xlsx file with toa results
    ss_toa()

    # create xlsx file with tri results
    ss_tri()

# main funtcion to test gui.py
def main():
    global x_max,y_max
    x_test_in = np.array([1,2,3,4,5])
    y_test_in = np.array([1,2,3,4,5])
    x_res_in = np.array([1.1,1.9,3.2,3.8,5.05])
    y_res_in = np.array([1.1,1.9,3.2,3.8,5.05])
    x_max_in = 6
    y_max_in = 6
    num_points_in = 4

    parabolas = np.empty((5,6), dtype=object)
    for i in range(0,5):
        for k in range(0,6,2):
            parabolas[i][k], parabolas[i][k+1] = rand_par(x_max_in)
    
    est_toa_in = np.empty((num_points_in,4))
    act_toa_in = np.empty((num_points_in,4))
    for r in range(0, num_points_in):
        for c in range(0,4):
            est_toa_in[r][c] = r
            act_toa_in[r][c] = r


    run(x_test_in,y_test_in,x_res_in,y_res_in,x_max_in,y_max_in,parabolas,num_points_in,est_toa_in, act_toa_in)

# Check if the script is being run as the main program
if __name__ == "__main__":
    main()


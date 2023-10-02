# main program for running the acoustic triangulation gui
# Robert Dugmore, Simon Carthew, and Si Teng Wu
# 30 Septermber 2023

# Some useful program notes:
# When the data collection thread adds data to the queue, it is always plotted.


import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading, time, queue

import random


# some useful global variables
plotSize = (640, 480)
samplingPeriod = 0.5

nextSamplingTime = time.time()

paused = True
readyManualControl = False
samplingPeriodDone = False
readyDataCollection = True
newPlot = False


threadQueue = queue.Queue(maxsize=1)

# generates random points to imitate the "localising" function, for testing purposes
def generate_random_points():
    time.sleep(1)
    return [random.uniform(0, 10), random.uniform(0, 8)]

# used to initialise the matplotlib plot that is shown in the gui
def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg



# used to read data from the mics and send it to application by adding to queue
def locate():
    global threadQueue
    
    try:
        threadQueue.put_nowait(generate_random_points())
    except queue.Empty:
        print("attempted to add multiple data to queue")

def setReadySamplingPeriod():
    global readyManualControl
    global samplingPeriodDone
    samplingPeriodDone = True
    readyManualControl = True



def continuous(event, values):
    global paused
    global nextSamplingTime
    global readyManualControl
    global samplingPeriodDone

    # process pause/play event in continuous mode
    if event == "-START-":
        paused = not paused
        if paused:
            window['-START-'].update(text='Resume')
        else:
            window['-START-'].update(text='Pause')
            nextSamplingTime = time.time() # set the new "start" sampling time
            readyManualControl = True
            samplingPeriodDone = True # ready for a sample    
        
    
    if samplingPeriodDone and not paused:
        samplingPeriodDone = False
        nextSamplingTime += samplingPeriod
        threading.Timer( nextSamplingTime - time.time(), setReadySamplingPeriod ).start()

def singleShot(event, values):
    global paused
    global window
    global readyManualControl

    paused = True

    window['-START-'].update(text='Start')

    if event == "-START-":
        readyManualControl = True
        window["-START-"].update(disabled=True)
    
def updatePlot(ax, data):
    ax.cla()
    ax.grid(True)
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 8])
    x = data[0]
    y = data[1]
    ax.plot(x, y ,'ro')


def main():
    global threadQueue
    global plotSize
    global readyManualControl
    global readyDataCollection
    global nextSamplingTime
    global newPlot
    global paused
    global window



    sg.theme('LightBlue6')   # Add a touch of color
    


    # All the stuff inside the window.
    layout = [  # canvas for matplotlib plot
                [sg.Canvas(size=plotSize, key="-CANVAS-")],

                # radio buttons for continuous / single shot modes
                [sg.Radio('Continuous', "CAPTUREMODE", default=True, key="-CONTINUOUS-", enable_events=True), 
                 sg.Radio("Single-Shot", "CAPTUREMODE", default=False, key="-SINGLESHOT-", enable_events=True)],

                # start / stop button
                [sg.Button('Start', key = "-START-")] ]

    # Create the Window
    window = sg.Window('Acoustic triangulation', layout, finalize=True)

    # create canvas to display matplotlib plot
    canvasElem = window['-CANVAS-'] 
    canvas = canvasElem.TKCanvas

    fig, ax = plt.subplots() # initialise matplotlib plot that will be displayed
    ax.grid(True)
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 8])
    figAgg = draw_figure(canvas, fig)


    # some booleans for control within while loop

    nextSamplingTime = time.time()


    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED: # if user closes window, exit loop
            break
        
        if values["-CONTINUOUS-"]:
            continuous(event, values)
        elif values["-SINGLESHOT-"]:
            singleShot(event, values)



        try:
            data = threadQueue.get_nowait() # attempt to get new data from queue
        except queue.Empty:
            data = None # no data in queue
        
        if data is not None:
            threadQueue.task_done() # set queue task to done
            readyDataCollection = True
            newPlot = True
        


        

        # implemented separately so that a separate sample rate flag can also be used
        if readyDataCollection and readyManualControl:
            readyDataCollection = False
            readyManualControl = False
            dataCollectionThread = threading.Thread(target=locate, args=(), daemon=True)
            dataCollectionThread.start()
        

        if newPlot:

            newPlot = False

            updatePlot(ax, data)
            
            figAgg.draw() # might need to take this out of the if

            # disable single-shot start button until data is ready to be plotted
            if values["-SINGLESHOT-"]:
                window["-START-"].update(disabled=False)


    window.close()


if __name__ == "__main__":
    main()
# main program for running the acoustic triangulation gui
# Robert Dugmore, Simon Carthew, and Si Teng Wu
# 30 Septermber 2023

# Some useful program notes:
# When the data collection thread adds data to the queue, it is always plotted.


import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import time
import queue
import localize as loc
import random
import next_byte


# some useful global variables
plotSize = (640, 480)
samplingPeriod = 1

micPositions = [[0, 0.5], [0.8, 0.5], [0, 0]]

nextSamplingTime = time.time()

paused = True
readyManualControl = False
samplingPeriodDone = False
readyDataCollection = True
newPlot = False


checkSyncDelay = False
plotHyperbolas = False

threadQueue = queue.Queue(maxsize=1)

# generates random points to imitate the "localising" function, for testing purposes


# used to initialise the matplotlib plot that is shown in the gui


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# used to read data from the mics and send it to application by adding to queue
def locate(startTime):
    global threadQueue
    global plotHyperbolas

    next_byte.inform_ready("192.168.137.132", "rpi1")
    next_byte.wait_trans("Main/rpi1_finnished.txt", "Main/rpi2_finnished.txt")

    try:
        result = loc.localize("Main/bytes/rpi1_next_byte.wav",
                         "Main/bytes/rpi2_next_byte.wav", micPositions, startTime,
                         hyperbola=plotHyperbolas, refTDOA=checkSyncDelay)
        threadQueue.put_nowait(result)
    except queue.Full:
        print("attempted to add multiple data to queue!!!")


def setReadySamplingPeriod():
    global readyManualControl
    global samplingPeriodDone
    samplingPeriodDone = True
    readyManualControl = not paused  # will only set to true if function is not paused


def continuous(event, values):
    global paused
    global nextSamplingTime
    global readyManualControl
    global samplingPeriodDone

    # process pause/play event in continuous mode
    if event == "-START-":
        paused = not paused
        if paused:
            mainWindow['-START-'].update(text='Resume')
        else:
            mainWindow['-START-'].update(text='Pause')
            nextSamplingTime = time.time()  # set the new "start" sampling time
            readyManualControl = True
            samplingPeriodDone = True  # ready for a sample

    if samplingPeriodDone and not paused:
        samplingPeriodDone = False
        nextSamplingTime += samplingPeriod
        threading.Timer(nextSamplingTime - time.time(),
                        setReadySamplingPeriod).start()


def singleShot(event, values):
    global paused
    global mainWindow
    global readyManualControl

    paused = True

    mainWindow['-START-'].update(text='Start')

    if event == "-START-":
        readyManualControl = True
        mainWindow["-START-"].update(disabled=True)


def updatePlot(ax, data):
    global plotHyperbolas
    ax.cla()
    ax.grid(True)
    ax.set_xlim([0, 0.8])
    ax.set_ylim([0, 0.5])
    x = data["results"][0]
    y = data["results"][1]
    ax.plot(x, y, 'ro')

    if plotHyperbolas and len(data["hyperbola"]) != 0:
        xc = data["hyperbola"][0]
        yc = data["hyperbola"][1]
        h1 = data["hyperbola"][2]
        h2 = data["hyperbola"][3]
        ax.contour(xc, yc, h1, [0], colors="b")
        ax.contour(xc, yc, h2, [0], colors="g")

    # add code here to plot hyperbolas based on data[2:4]



def updateSamplingFrequency(values):
    global mainWindow
    global samplingPeriod

    try:
        newVal = float(values["-SAMPLINGVAL-"])
        if values["-USESAMPLINGFREQ-"]:
            samplingPeriod = 1/newVal
        if values["-USESAMPLINGPERIOD-"]:
            samplingPeriod = newVal*1e-3

        mainWindow["-MESSAGE-"].update(value="Sample rate updated")

    except ValueError:
        mainWindow["-MESSAGE-"].update(value="Invalid sample rate entered")

def makeMainWindow():
    # All the stuff inside the mainWindow.
    layout = [  # canvas for matplotlib plot
        [sg.Canvas(size=plotSize, key="-CANVAS-")],

        # result of sync test and system timing
        [sg.Text("Synchronisation delay: N/A", size = (31, 1), key="-SYNCDELAY-"), 
        sg.Text("Update time: N/A", size = (20, 1), key="-UPDATETIME-")],

        # start / stop button
        [sg.Button('Start', key="-START-")],

        # Horizontal separator
        [sg.HorizontalSeparator()],

        # radio buttons for continuous / single shot modes
        [sg.Radio('Continuous', "CAPTUREMODE", default=True, key="-CONTINUOUS-", enable_events=True),
            sg.Radio("Single-Shot", "CAPTUREMODE", default=False, key="-SINGLESHOT-", enable_events=True)],

        [sg.Checkbox("Plot hyperbolas", default=False, key="-PLOTHYPERBOLAS-"),
         sg.Checkbox("Calculate synchronisation delay", default=False, key="-CHECKSYNCDELAY-")],
        # Horizontal separator
        [sg.HorizontalSeparator()],

        # continuous-time sampling frequency
        [sg.Text("Sampling rate (continuous mode)"),
            sg.Radio("Frequency (Hz)", "SAMPLINGRATEMODE",
                     default=True, key="-USESAMPLINGFREQ-"),
            sg.Radio("Period (ms)", "SAMPLINGRATEMODE",
                     default=False, key="-USESAMPLINGPERIOD-"),
            sg.Input(default_text=1, size=(8, 1), key="-SAMPLINGVAL-"), sg.Button("Update", key="-UPDATESAMPLINGVAL-")],

        # Horizontal separator
        [sg.HorizontalSeparator()],

        [sg.Button("Subsystem tests", key="-TESTS-")],

        # output message
        [sg.Text("", key="-MESSAGE-")]
    ]

    return sg.Window('Acoustic triangulation', layout, finalize=True)

def makeTestsWindow():
    layout = [
        ### Sync test
        [sg.Text("Pi Synchronisation Test")],

        [sg.Button("Go", key="-SYNCTEST-"), sg.Text("", key="-TIME1-"), sg.Text("", key="-TIME2-")],

        [sg.HorizontalSeparator()],

        ### Signal acquisition test
        [sg.Text("Signal Acquisition Test")], 

        [sg.Button("Go", key="-SIGNALTEST-")], 
         
        [sg.HorizontalSeparator()], 

        ### TDOA test
        [sg.Text("TDOA test")], 

        [sg.Button("Go", key="-TDOATEST-"), sg.Text("x: "), sg.Input(key="-TDOATESTX-"), 
         sg.Text("y: "), sg.Input(key="-TDOATESTY-")], 

        [sg.Text("Estimated TDOAs: ", key="-ESTTDOAS-")], 
        [sg.Text("Actual TDOAS: ", key="-ACTTDOAS-")],

        [sg.HorizontalSeparator()],

        ### Triangulation test
        [sg.Text("Triangulation test")], 

        [sg.Button("Go", key="-TRITEST-"), sg.Text("TDOA 1: "), sg.Input(key="-TRITESTTDOA1-"), 
         sg.Text("TDOA 2: "), sg.Input(key="-TRITESTTDOA2-")]
         
    ]

    return sg.Window('Tests window', layout, finalize=True, modal=True)
    
def openTestsWindow():
    global testsWindow


    testsWindow = makeTestsWindow()
    while True:
        event, values = testsWindow.read()


        if event == sg.WIN_CLOSED:
            break
        
    testsWindow.close()

def main():
    global threadQueue
    global plotSize
    global readyManualControl
    global readyDataCollection
    global nextSamplingTime
    global newPlot
    global plotHyperbolas
    global paused
    global mainWindow
    global checkSyncDelay

    sg.theme('LightBlue6')   # Add a touch of color


    # Create the main window
    mainWindow = makeMainWindow()

    # create canvas to display matplotlib plot
    canvasElem = mainWindow['-CANVAS-']
    canvas = canvasElem.TKCanvas

    fig, ax = plt.subplots()  # initialise matplotlib plot that will be displayed
    ax.grid(True)
    ax.set_xlim([0, 0.8])
    ax.set_ylim([0, 0.5])
    figAgg = draw_figure(canvas, fig)

    # some booleans for control within while loop

    nextSamplingTime = time.time()

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = mainWindow.read(timeout=100)
        if event == sg.WIN_CLOSED:  # if user closes mainWindow, exit loop
            break
        
        if event == "-TESTS-":
            openTestsWindow()

        if values["-CONTINUOUS-"]:
            continuous(event, values)
        elif values["-SINGLESHOT-"]:
            singleShot(event, values)

        if event == "-UPDATESAMPLINGVAL-":
            updateSamplingFrequency(values)

        try:
            data = threadQueue.get_nowait()  # attempt to get new data from queue
        except queue.Empty:
            data = None  # no data in queue

        if data is not None:
            threadQueue.task_done()  # set queue task to done
            readyDataCollection = True
            newPlot = True

        # implemented separately so that a separate sample rate flag can also be used
        if readyDataCollection and readyManualControl:
            startTime = time.time()

            checkSyncDelay = values["-CHECKSYNCDELAY-"]
            plotHyperbolas = values["-PLOTHYPERBOLAS-"]
            readyDataCollection = False
            readyManualControl = False
            dataCollectionThread = threading.Thread(
                target=locate, args=(startTime), daemon=True)
            dataCollectionThread.start()

        # known problem: if plotting is slower than data collection,
        if newPlot and len(data["result"]) != 0:
            newPlot = False

            updatePlot(ax, data)

            if checkSyncDelay and len(data["reftdoa"]) != 0:

                syncDelay = data["reftdoa"][0] * 1e3
                message = "Syncrhonistaion delay: " + \
                    "{:.3f}".format(syncDelay) + " ms"

                mainWindow["-SYNCDELAY-"].update(value=message)
            else:
                mainWindow["-SYNCDELAY-"].update(
                    value="Syncrhonisation delay: N/A")
                
            startTime = data["times"][0]
            

            figAgg.draw()  # might need to take this out of the if

            endTime = time.time()

            message = "Update time: " + \
                "{:.3f}".format(endTime - startTime) + " s"
            mainWindow["-UPDATETIME-"].update(value=message)

            

            # disable single-shot start button until data is ready to be plotted
            if values["-SINGLESHOT-"]:
                mainWindow["-START-"].update(disabled=False)

    mainWindow.close()


if __name__ == "__main__":
    main()

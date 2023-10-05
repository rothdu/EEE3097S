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
import next_byte
import random
import os
import subsystems


# some useful global variables
plotSize = (640, 480)
samplingPeriod = 1

micPositions = [[0, 0.5], [0.8, 0.5], [0, 0]]

rpi1_fin_path = "Main/rpi1_finnished.txt"
rpi2_fin_path = "Main/rpi2_finnished.txt"

rpi1_byte_path = "Main/bytes/rpi1_next_byte.wav"
rpi2_byte_path = "Main/bytes/rpi2_next_byte.wav"

rpi1_ip = "192.168.137.132"

nextSamplingTime = time.time()

mode = "continuous"

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
    global rpi1_fin_path
    global rpi2_fin_path
    global rpi1_byte_path
    global rpi2_byte_path
    global rpi1_ip

    next_byte.inform_ready(rpi1_ip, "rpi1")
    next_byte.wait_trans(rpi1_fin_path, rpi2_fin_path)

    try:
        result = loc.localize(rpi1_byte_path,
                              rpi2_byte_path, micPositions, startTime,
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
    x = data["result"][0]
    y = data["result"][1]
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


def updateMicPositions(values):
    try:
        micPositions[0][0] = float(values["-REFMICPOSX-"])
        micPositions[0][1] = float(values["-REFMICPOSY-"])
        micPositions[1][0] = float(values["-PI1MICPOSX-"])
        micPositions[1][1] = float(values["-PI1MICPOSY-"])
        micPositions[2][0] = float(values["-PI2MICPOSX-"])
        micPositions[2][1] = float(values["-PI2MICPOSY-"])

        mainWindow["-MESSAGE-"].update(value="Mic positions updated")
    except ValueError:
        mainWindow["-MESSAGE-"].update(value="Invalid mic position entered")


def signalAcquisitionTest(event, values):
    global testsWindow
    global testsPlotWindow
    global rpi1_fin_path
    global rpi2_fin_path
    global rpi1_byte_path
    global rpi2_byte_path
    global rpi1_ip

    next_byte.inform_ready(rpi1_ip, "rpi1")
    next_byte.wait_trans(rpi1_fin_path, rpi2_fin_path)

    results = loc.signalAquisitionTest(rpi1_byte_path, rpi2_byte_path)


    testsPlotWindow = makeTestsPlotWindow("Signal Acquisition Test")

    canvasElem = testsPlotWindow['-TESTSCANVAS-']
    canvas = canvasElem.TKCanvas

    fig, axes = plt.subplots(2, 2)  # initialise matplotlib plot that will be displayed

    # can add additional plotting here
    axes[0][0].plot(results["original"][0], color = "b")
    axes[0][1].plot(results["original"][1], color = "g")
    axes[1][0].plot(results["original"][2], color = "r")
    axes[1][1].plot(results["original"][3], color = "m")

    figAgg = draw_figure(canvas, fig)

    while True:
        event, values = testsPlotWindow.read()

        if event == sg.WIN_CLOSED:
            testsPlotWindow.close()
            break

    testsPlotWindow = makeTestsPlotWindow("Signal Acquisition Test")

    canvasElem = testsPlotWindow['-TESTSCANVAS-']
    canvas = canvasElem.TKCanvas

    fig, axes = plt.subplots(2, 2)  # initialise matplotlib plot that will be displayed

    # can add additional plotting here
    axes[0][0].plot(results["processed"][0], color = "b")
    axes[0][1].plot(results["processed"][1], color = "g")
    axes[1][0].plot(results["processed"][2], color = "r")
    axes[1][1].plot(results["processed"][3], color = "m")

    figAgg = draw_figure(canvas, fig)

    while True:
        event, values = testsPlotWindow.read()

        if event == sg.WIN_CLOSED:
            testsPlotWindow.close()
            break

def tdoaTest(event, values):
    global testsWindow
    global micPositions
    global rpi1_byte_path
    global rpi2_byte_path

    try:
        x = float(values["-TDOATESTX-"])
        y = float(values["-TDOATESTY-"])

        result = loc.tdoaTest(x, y, rpi1_byte_path, rpi2_byte_path, micPositions)

        est = "{:.7f} {:.7f}".format(result["estiTdoa"][0], result["estiTdoa"][1])
        act = "{:.7f} {:.7f}".format(result["actualTdoa"][0], result["actualTdoa"][1])
        err = "{:.7f} {:.7f}".format(result["percentError"][0], result["percentError"][1])

        
    
    except ValueError:
        est = "Invalid coordinates"
        act = "Invalid coordinates"
        err = "Invalid coordinates"
    
    testsWindow["-ESTTDOAS-"].update(value = est)
    testsWindow["-ACTTDOAS-"].update(value = act)
    testsWindow["-TDOAERR-"].update(value = err)




def makeMainWindow():
    # All the stuff inside the mainWindow.
    layout = [  # canvas for matplotlib plot
        [sg.Canvas(size=plotSize, key="-CANVAS-")],

        # result of sync test and system timing
        [sg.Text("Update time: N/A", size=(20, 1), key="-UPDATETIME-"),
         sg.Text("", size=(31, 1), key="-SYNCDELAY-")],

        # start / stop button
        [sg.Button('Start', key="-START-", size=(6, 1)),
         sg.Button('Config', key="-CONFIG-", size=(6, 1)),
         sg.Button('Tests', key="-TESTS-", size=(6, 1))],

        # output message
        [sg.Text("", key="-MESSAGE-", enable_events=True)]

    ]

    return sg.Window('Acoustic triangulation', layout, finalize=True, location=(700, 0))


def makeTestsWindow():
    layout = [
        # Sync test
        [sg.Text("Pi Synchronisation Test")],

        [sg.Button("Go", key="-SYNCTEST-"), sg.Text("",key="-TIME1-"), sg.Text("", key="-TIME2-")],

        [sg.HorizontalSeparator()],

        # Signal acquisition test
        [sg.Text("Signal Acquisition Test")],

        [sg.Button("Go", key="-SIGNALTEST-")],

        [sg.HorizontalSeparator()],

        # TDOA test
        [sg.Text("TDOA test")],

        [sg.Button("Go", key="-TDOATEST-"), sg.Text("x: "), sg.Input(key="-TDOATESTX-"),
         sg.Text("y: "), sg.Input(key="-TDOATESTY-")],

        
        [sg.Text("Theoretical TDOAS: ", size=(20, 1)), sg.Text("", key="-ACTTDOAS-")],
        [sg.Text("Calculated TDOAs: ", size=(20,1)), sg.Text("", key="-ESTTDOAS-")],
        [sg.Text("Percentage error: ", size=(20, 1)), sg.Text("", key="-TDOAERR-")],

        [sg.HorizontalSeparator()],

        # Triangulation test
        [sg.Text("Triangulation test")],

        [sg.Button("Go", key="-TRITEST-"), sg.Text("TDOA 1: "), sg.Input(key="-TRITESTTDOA1-"),
         sg.Text("TDOA 2: "), sg.Input(key="-TRITESTTDOA2-")]

    ]

    return sg.Window('Tests window', layout, finalize=True, modal=True, location=(700, 0))


def makeTestsPlotWindow(windowName):
    global plotSize
    layout = [  # canvas for matplotlib plot
        [sg.Canvas(size=plotSize, key="-TESTSCANVAS-")],
    ]

    return sg.Window(windowName, layout, finalize=True, location=(700, 0), modal=True)

def makeConfigWindow():
    layout = [

        # radio buttons for continuous / single shot modes
        [sg.Radio('Continuous', "CAPTUREMODE", default=True, key="-CONTINUOUS-", enable_events=True),
         sg.Radio("Single-Shot", "CAPTUREMODE", default=False, key="-SINGLESHOT-", enable_events=True)],


        # checkboxes for plotting hyperbolas
        [sg.Checkbox("Plot hyperbolas", default=False, key="-PLOTHYPERBOLAS-", enable_events=True)],

        # show sync delay
        [sg.Checkbox("Calculate synchronisation delay", default=False, key="-CHECKSYNCDELAY-", enable_events=True)],

        # Horizontal separator
        [sg.HorizontalSeparator()],

        # continuous-time sampling frequency
        [sg.Text("Sampling rate (continuous mode)"),
         sg.Radio("Frequency (Hz)", "SAMPLINGRATEMODE",
                  default=True, key="-USESAMPLINGFREQ-"),
         sg.Radio("Period (ms)", "SAMPLINGRATEMODE",
                  default=False, key="-USESAMPLINGPERIOD-"),
         sg.Input(default_text=1, size=(8, 1), key="-SAMPLINGVAL-"),
         sg.Button("Update", key="-UPDATESAMPLINGVAL-")],

        
        # Horizontal separator
        [sg.HorizontalSeparator()],

        # mic positions
        [sg.Text("Mic positions")],
        [sg.Text("Reference: ", size=(16, 1)), sg.Text("x: "),
         sg.Input(key="-REFMICPOSX-", size=(10, 1)), sg.Text("y: "),
         sg.Input(key="-REFMICPOSY-", size=(10, 1))],
        [sg.Text("Pi 1 (2nd mic): ", size=(16, 1)), sg.Text("x: "),
         sg.Input(key="-PI1MICPOSX-", size=(10, 1)), sg.Text("y: "),
         sg.Input(key="-PI1MICPOSY-", size=(10, 1))],
        [sg.Text("Pi 2 (2nd mic): ", size=(16, 1)), sg.Text("x: "),
         sg.Input(key="-PI2MICPOSX-", size=(10, 1)), sg.Text("y: "),
         sg.Input(key="-PI2MICPOSY-", size=(10, 1))],
        [sg.Button("Update", key="-UPDATEMICPOS-")],

    ]

    return sg.Window('Config', layout, finalize=True, location=(700, 0))


def main():
    global threadQueue
    global plotSize
    global readyManualControl
    global readyDataCollection
    global nextSamplingTime
    global newPlot
    global plotHyperbolas
    global paused
    global checkSyncDelay
    global mode

    global mainWindow
    global testsWindow
    global configWindow

    # remove "rpi finished" things
    if os.path.exists(rpi1_fin_path):
        os.remove(rpi1_fin_path)
    if os.path.exists(rpi2_fin_path):
        os.remove(rpi2_fin_path)

    sg.theme('LightBlue6')   # Add a touch of color

    # Create the main window
    mainWindow = makeMainWindow()
    configWindow = None
    testsWindow = None

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
        window, event, values = sg.read_all_windows(timeout=100)

        if event == sg.WIN_CLOSED:  # if user closes mainWindow, exit loop
            if window == mainWindow:
                break
            if window == configWindow:
                configWindow.close()
                configWindow = None
            if window == testsWindow:
                testsWindow.close()
                testsWindow = None

        # Easter egg
        if event == "-MESSAGE-":
            mainWindow.close()
            configWindow.close()
            sg.theme(random.choice(sg.theme_list()))
            mainWindow = makeMainWindow()
            configWindow = makeConfigWindow()

            canvasElem = mainWindow['-CANVAS-']
            canvas = canvasElem.TKCanvas
            fig, ax = plt.subplots()  # initialise matplotlib plot that will be displayed
            ax.grid(True)
            ax.set_xlim([0, 0.8])
            ax.set_ylim([0, 0.5])
            figAgg = draw_figure(canvas, fig)

        if event == "-TESTS-" and testsWindow is None:
            testsWindow = makeTestsWindow()

        if event == "-CONFIG-" and configWindow is None:
            configWindow = makeConfigWindow()

        # update config settings
        if window == configWindow and values is not None:
            if values["-CONTINUOUS-"]:
                mode = "continuous"

            elif values["-SINGLESHOT-"]:
                mode = "singleshot"

            checkSyncDelay = values["-CHECKSYNCDELAY-"]
            plotHyperbolas = values["-PLOTHYPERBOLAS-"]

        if event == "-UPDATESAMPLINGVAL-":
            updateSamplingFrequency(values)

        if event == "-UPDATEMICPOS-":
            updateMicPositions(values)

        ### IMPLEMENTATION OF TEST WINDOW EVENTS
        if event == "-TDOATEST-":
            tdoaTest(event, values)        

        if event == "-SIGNALTEST-":
            signalAcquisitionTest(event, values)
        
        ### Implementation of main window events

        if mode == "continuous":
            continuous(event, values)
        elif mode == "singleshot":
            singleShot(event, values)

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
            readyDataCollection = False
            readyManualControl = False
            dataCollectionThread = threading.Thread(
                target=locate, args=[startTime], daemon=True)
            dataCollectionThread.start()

        # known problem: if plotting is slower than data collection,
        if newPlot:
            newPlot = False
            if len(data["result"]) == 0:

                # print an error message based on localise function
                if len(data("errorMessage")) == 0:
                    mainWindow["-MESSAGE-"].update(value="Error: Unknown error")
                else:
                    mainWindow["-MESSAGE-"].update(value= ("Error: " + data["errorMessage"][0]))
            else:

                updatePlot(ax, data)

                if checkSyncDelay and len(data["reftdoa"]) != 0:

                    syncDelay = data["reftdoa"][0] * 1e3
                    message = "Syncrhonistaion delay: " + \
                        "{:.3f}".format(syncDelay) + " ms"

                    mainWindow["-SYNCDELAY-"].update(value=message)
                elif not checkSyncDelay:
                    mainWindow["-SYNCDELAY-"].update(
                        value="")
                else:
                    mainWindow["-SYNCDELAY-"].update(
                        value="Synchronisation delay: Error")

                startTime = data["times"][0]

                figAgg.draw()  # might need to take this out of the if

                endTime = time.time()

                updateTime = "Update time: " + \
                    "{:.3f}".format(endTime - startTime) + " s"
                mainWindow["-UPDATETIME-"].update(value=updateTime)

                mainWindow["-MESSAGE-"].update("Plotted point")

            # disable single-shot start button until data is ready to be plotted
            if mode == "singleshot":
                mainWindow["-START-"].update(disabled=False)

    mainWindow.close()


if __name__ == "__main__":
    main()

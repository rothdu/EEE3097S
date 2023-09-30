# main program for running the acoustic triangulation gui
# Robert Dugmore, Simon Carthew, and Si Teng Wu
# 30 Septermber 2023

import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading, time, queue

import random


# some useful global variables
plotSize = (640, 480)
samplingPeriod = 0.5
readySamplingPeriod = True
nextSamplingTime = time.time()


threadQueue = queue.Queue(maxsize=1)

CANVAS_KEY = '-CANVAS-'

def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def generate_random_points():
    return [random.uniform(0, 10), random.uniform(0, 8)]

# used to read data from the queue and send it to application by adding to queue
def locate():
    global threadQueue
    
    sleeptime = random.uniform(0, 1)
    time.sleep(sleeptime)
    try:
        threadQueue.put_nowait(generate_random_points())
    except queue.Empty:
        print("attempted to add multiple data to queue")

def set_readySamplingPeriod():
    global readySamplingPeriod
    readySamplingPeriod = True

def main():
    global threadQueue
    global plotSize
    global readySamplingPeriod


    sg.theme('LightBlue6')   # Add a touch of color
    


    # All the stuff inside your window.
    layout = [  [sg.Text('Acoustic triangulation')],
                [sg.Canvas(size=plotSize, key=CANVAS_KEY)],
                [sg.Button('Start'), sg.Button('Pause'), sg.Button('Stop')] ]

    # Create the Window
    window = sg.Window('Acoustic triangulation', layout, finalize=True)

    canvasElem = window['-CANVAS-']
    canvas = canvasElem.TKCanvas

    fig, ax = plt.subplots()
    ax.grid(True)
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 8])
    figAgg = draw_figure(canvas, fig)


    # some booleans for control within while loop

    readyDataCollection = True
    newPlot = False

    global nextSamplingTime
    nextSamplingTime = time.time()

    ######## temp checker
    prevTime = time.time()

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED: # if user closes window, exit loop
            break

        try:
            data = threadQueue.get_nowait() # attempt to get new data from queue
        except queue.Empty:
            data = None # no data in queue
        
        if data is not None:
            threadQueue.task_done() # set queue task to done
            readyDataCollection = True
            newPlot = True

        if readySamplingPeriod:
            nextSamplingTime += samplingPeriod
            threading.Timer( nextSamplingTime - time.time(), set_readySamplingPeriod ).start()

        # implemented separately so that a separate sample rate flag can also be used
        if readyDataCollection and readySamplingPeriod:
            readyDataCollection = False
            readySamplingPeriod = False
            thread_id = threading.Thread(target=locate, args=(), daemon=True)
            thread_id.start()
        
        if newPlot:

            newPlot = False

            ax.cla()
            ax.grid(True)
            ax.set_xlim([0, 10])
            ax.set_ylim([0, 8])
            x = data[0]
            y = data[1]
            ax.plot(x, y ,'ro')


            figAgg.draw() # might need to take this out of the if


    window.close()


if __name__ == "__main__":
    main()
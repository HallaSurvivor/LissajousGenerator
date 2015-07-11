"""
Dynamically create Lissajous curves based on user inputs.

Lissajous curves follow the parametric equations:

X = Asin(at + delta)
Y = Bsin(bt)

A and B are scalar multiples corresponding to the amplitude of waves
a and b correspond to the angular frequency of waves
delta corresponds to the phase difference between the waves

Together these form a set of images that correspond to taking two waves
and super imposing them at 90 degrees.

This script will dynamically create the curves based on user input, and
play tones corresponding to the notes given.

Thanks to Ella for the idea :)
"""

import Tkinter as tk
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pyaudio
matplotlib.use("TkAgg")


class LissajousGenerator(tk.Frame):
    """
    The main class of the program.

    Creates a tkinter window with sliders and boxes
    for all the variables (defined below)

    Also includes two dropdowns containing notes
    just tuned to A major using 7-limit just intonation.
    Selecting them will automatically override the settings.

    A is the Wave1 (W1) amplitude
    B is the Wave2 (W2) amplitude

    a is the W1 frequency
    b is the W2 frequency

    delta is the phase difference in the waves

    Thanks to Jan Bodar from zetacode.com for the basis of this code
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background="white")
        self.parent = parent

        self.player = pyaudio.PyAudio()

        #Define variables
        self.A = tk.DoubleVar()
        self.B = tk.DoubleVar()
        self.a = tk.DoubleVar()
        self.b = tk.DoubleVar()
        self.delta = tk.DoubleVar()

        #Set variables
        self.A.set(10)
        self.B.set(10)
        self.a.set(3)
        self.b.set(2)
        self.delta.set(0)

        #Define constants
        self.notes = ['A4', 'A#4', 'B4', 'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5',
                      'A5', 'A#5', 'B5', 'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6',
                      'A6', 'A#6', 'B6', 'C7', 'C#7', 'D7', 'D#7', 'E7', 'F7', 'F#7', 'G7', 'G#7']

        self.note_dict = {'A4': 1.0, 'A#4': 16.0/15.0, 'B4': 8.0/7.0, 'C5': 6.0/5.0, 'C#5': 5.0/4.0,
                          'D5': 4.0/3.0, 'D#5': 10.0/7.0, 'E5': 3.0/2.0, 'F5': 8.0/5.0, 'F#5': 5.0/3.0,
                          'G5': 7.0/4.0, 'G#5': 15.0/8.0, 'A5': 2.0, 'A#5': 32.0/15.0, 'B5': 16.0/7.0,
                          'C6': 12.0/5.0, 'C#6': 5.0/2.0, 'D6': 8.0/3.0, 'D#6': 20.0/7.0, 'E6': 3.0,
                          'F6': 16.0/5.0, 'F#6': 10.0/3.0, 'G6': 7.0/2.0, 'G#6': 15.0/4.0, 'A6': 4.0,
                          'A#6': 64.0/15.0, 'B6': 32.0/7.0, 'C7': 24.0/5.0, 'C#7': 5.0, 'D7': 16.0/3.0,
                          'D#7': 40.0/7.0, 'E7': 6.0, 'F7': 32.0/5.0, 'F#7': 20.0/3.0, 'G7': 7.0, 'G#7': 15.0/2.0}

        self.fs = 44100
        self.volume = 0.5
        self.duration = 5

        self.initUI()

    def initUI(self):
        """
        Create the GUI
        """

        self.parent.title("Lissajous Generator")
        self.pack(fill=tk.BOTH, expand=True)

        varsliders = VariableSliders(self)
        varsliders.grid(row=0, column=0, padx=10, pady=2)

        notevars = NoteVariables(self)
        notevars.grid(row=0, column=1, padx=10, pady=2)

        plot = Plot(self)
        plot.grid(row=1, column=0, columnspan=2, padx=10, pady=2)

    def changeA(self, value):
        self.A.set(float(value))

    def changeB(self, value):
        self.B.set(float(value))

    def changea(self, value):
        self.a.set(float(value))

    def changeb(self, value):
        self.b.set(float(value))

    def changedelta(self, value):
        self.delta.set(float(value))

    def choose_note1(self, note):
        self.A.set(5)

        sender = note.widget
        idx = sender.curselection()
        self.a.set(self.note_dict[sender.get(idx)])

        self.delta.set(0)

    def choose_note2(self, note):
        self.B.set(5)

        sender = note.widget
        idx = sender.curselection()
        self.b.set(self.note_dict[sender.get(idx)])

        self.delta.set(0)


class VariableSliders(tk.Frame):
    """
    A frame containing the variable labels, sliders, and entry boxes
    """

    def __init__(self, parent):
        """
        I turned the sliders off for aesthetic reasons. Changing the entry did not update the slider
        """
        tk.Frame.__init__(self, parent, background="white")
        self.parent = parent

        tk.Label(self, text="A amplitude").grid(row=1, column=0)
        # Aslider = tk.Scale(self, from_=0, to=10, orient=tk.HORIZONTAL, resolution=0.01, command=self.parent.changeA)
        # Aslider.grid(row=1, column=1)
        Aentry = tk.Entry(self, textvariable=self.parent.A)
        Aentry.grid(row=1, column=2)

        tk.Label(self, text="B amplitude").grid(row=2, column=0)
        # Bslider = tk.Scale(self, from_=0, to=10, orient=tk.HORIZONTAL, resolution=0.01, command=self.parent.changeB)
        # Bslider.grid(row=2, column=1)
        Bentry = tk.Entry(self, textvariable=self.parent.B)
        Bentry.grid(row=2, column=2)

        tk.Label(self, text="A frequency").grid(row=3, column=0)
        # aslider = tk.Scale(self, from_=440, to=1760, orient=tk.HORIZONTAL, resolution=0.01, command=self.parent.changea)
        # aslider.grid(row=3, column=1)
        aentry = tk.Entry(self, textvariable=self.parent.a)
        aentry.grid(row=3, column=2)

        tk.Label(self, text="A frequency").grid(row=4, column=0)
        # bslider = tk.Scale(self, from_=440, to=1760, orient=tk.HORIZONTAL, resolution=0.01, command=self.parent.changeb)
        # bslider.grid(row=4, column=1)
        bentry = tk.Entry(self, textvariable=self.parent.b)
        bentry.grid(row=4, column=2)

        tk.Label(self, text="Phase Shift").grid(row=5, column=0)
        # deltaslider = tk.Scale(self, from_=0, to=6.28, orient=tk.HORIZONTAL, resolution=0.01, command=self.parent.changedelta)
        # deltaslider.grid(row=5, column=1)
        deltaentry = tk.Entry(self, textvariable=self.parent.delta)
        deltaentry.grid(row=5, column=2)

        self.pack()


class NoteVariables(tk.Frame):
    """
    A frame for storing the note selection box
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background="white")
        self.parent = parent

        note1frame = tk.Frame(self)

        tk.Label(note1frame, text="Note 1").pack(side=tk.TOP)
        note1 = tk.Listbox(note1frame)
        for note in self.parent.notes:
            note1.insert(tk.END, note)
        note1.bind("<<ListboxSelect>>", self.parent.choose_note1)
        note1.pack(side=tk.LEFT)
        note1scroll = tk.Scrollbar(note1frame, orient=tk.VERTICAL)
        note1scroll.pack(side=tk.RIGHT, fill=tk.Y)

        note1scroll.configure(command=note1.yview)
        note1.configure(yscrollcommand=note1scroll.set)

        note1frame.pack(side=tk.LEFT)
        note2frame = tk.Frame(self)

        tk.Label(note2frame, text="Note 2").pack(side=tk.TOP)
        note2 = tk.Listbox(note2frame)

        for note in self.parent.notes:
            note2.insert(tk.END, note)

        note2.bind("<<ListboxSelect>>", self.parent.choose_note2)
        note2.pack(side=tk.LEFT)
        note2scroll = tk.Scrollbar(note2frame, orient=tk.VERTICAL)
        note2scroll.pack(side=tk.RIGHT, fill=tk.Y)

        note2scroll.configure(command=note2.yview)
        note2.configure(yscrollcommand=note2scroll.set)

        note2frame.pack(side=tk.LEFT)

        self.pack()


class Plot(tk.Frame):
    """
    A frame for storing the plot generated by matplotlib
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background="white")
        self.parent = parent

        T = [float(num)/100.0 for num in range(0, 10001)]
        X = [self.parent.A.get()*np.sin(self.parent.a.get()*t + self.parent.delta.get()) for t in T]
        Y = [self.parent.B.get()*np.sin(self.parent.b.get()*t) for t in T]

        #Create plot
        f = Figure(figsize=(5, 5), dpi=100)
        plot = f.add_subplot(111)
        self.graph, = plot.plot(X, Y)

        self.canvas = FigureCanvasTkAgg(f, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.Button(self, text='Refresh Image', command=self.refresh).pack(side=tk.BOTTOM)

        self.pack()

    def refresh(self):
        T = [float(num)/100.0 for num in range(0, 10001)]
        X = [self.parent.A.get()*np.sin(self.parent.a.get()*t + self.parent.delta.get()) for t in T]
        Y = [self.parent.B.get()*np.sin(self.parent.b.get()*t) for t in T]

        self.graph.set_data(X, Y)
        ax = self.canvas.figure.axes[0]
        ax.set_xlim(min(X), max(X))
        ax.set_ylim(min(Y), max(Y))

        self.canvas.draw()

        self.play_notes()

    def play_notes(self):
        """
        Play the selected notes with pyaudio

        Thanks to stackoverflow ivan_onys for the basis of this code
        """

        sampleA = (np.sin(2*np.pi*np.arange(self.parent.fs*self.parent.duration)*self.parent.a.get()*440/self.parent.fs)).astype(np.float32)
        sampleB = (np.sin(2*np.pi*np.arange(self.parent.fs*self.parent.duration)*self.parent.b.get()*440/self.parent.fs)).astype(np.float32)
        stream = self.parent.player.open(format=pyaudio.paFloat32, channels=1, rate=self.parent.fs, output=True)

        to_play = (sampleA + sampleB)/2

        stream.write(self.parent.volume*to_play)

        stream.stop_stream()
        stream.close()

root = tk.Tk()
root.geometry("660x800")
app = LissajousGenerator(root)
root.mainloop()
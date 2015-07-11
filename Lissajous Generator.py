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
"""

import Tkinter as tk
import numpy as np
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import pyaudio

volume = 0.5
fs = 44100
duration = 1.0
f = 440.0


# The land of please-do-not-touch
matplotlib.use("TkAgg")


class LissajousGenerator(tk.Frame):
    """
    The main class of the program.

    Creates a tkinter window with sliders and boxes
    for all the variables (defined below)

    Also includes two dropdowns containing notes
    just tuned to A major. Selecting them will
    automatically override the settings.

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

        #Define variables
        self.A = tk.DoubleVar()
        self.B = tk.DoubleVar()
        self.a = tk.DoubleVar()
        self.b = tk.DoubleVar()
        self.delta = tk.DoubleVar()

        self.Astr = tk.StringVar()
        self.Bstr = tk.StringVar()
        self.astr = tk.StringVar()
        self.bstr = tk.StringVar()
        self.deltastr = tk.StringVar()

        #Set variables
        self.A.set(10)
        self.B.set(10)
        self.a.set(3)
        self.b.set(2)
        self.delta.set(0)

        self.Astr.set('10')
        self.Bstr.set('10')
        self.astr.set('3')
        self.bstr.set('2')
        self.deltastr.set('0')

        #Define constants
        self.notes = ['A4', 'A#4', 'B4', 'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4',
                      'A5', 'A#5', 'B5', 'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5',
                      'A6', 'A#6', 'B6', 'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6']

        self.note_dict = {'A4': 440}

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

    def choose_note2(self, note):
        self.A.set(5)

        sender = note.widget
        idx = sender.curselection()
        self.a.set(self.note_dict[sender.get(idx)])


class VariableSliders(tk.Frame):
    """
    A frame containing the variable labels, sliders, and entry boxes
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background="white")
        self.parent = parent

        Alabel = tk.Label(self, text="A amplitude").grid(row=1, column=0)
        Aslider = tk.Scale(self, from_=0, to=10, orient=tk.HORIZONTAL,
                           resolution=0.01, command=self.parent.changeA).grid(row=1, column=1)
        Aentry = tk.Entry(self, textvariable=self.parent.Astr).grid(row=1, column=2)

        Blabel = tk.Label(self, text="B amplitude").grid(row=2, column=0)
        Bslider = tk.Scale(self, from_=0, to=10, orient=tk.HORIZONTAL,
                           resolution=0.01, command=self.parent.changeB).grid(row=2, column=1)
        Bentry = tk.Entry(self, textvariable=self.parent.Bstr).grid(row=2, column=2)

        alabel = tk.Label(self, text="A frequency").grid(row=3, column=0)
        aslider = tk.Scale(self, from_=440, to=1760, orient=tk.HORIZONTAL,
                           resolution=0.01, command=self.parent.changea).grid(row=3, column=1)
        aentry = tk.Entry(self, textvariable=self.parent.astr).grid(row=3, column=2)

        blabel = tk.Label(self, text="A frequency").grid(row=4, column=0)
        bslider = tk.Scale(self, from_=440, to=1760, orient=tk.HORIZONTAL,
                           resolution=0.01, command=self.parent.changeb).grid(row=4, column=1)
        bentry = tk.Entry(self, textvariable=self.parent.bstr).grid(row=4, column=2)

        deltalabel = tk.Label(self, text="Phase Shift").grid(row=5, column=0)
        deltaslider = tk.Scale(self, from_=0, to=6.28, orient=tk.HORIZONTAL,
                               resolution=0.01, command=self.parent.changedelta).grid(row=5, column=1)
        deltaentry = tk.Entry(self, textvariable=self.parent.deltastr).grid(row=5, column=2)

        self.pack()


class NoteVariables(tk.Frame):
    """
    A frame for storing the note selection box
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background="white")
        self.parent = parent

        note1frame = tk.Frame(self)

        note1label = tk.Label(note1frame, text="Note 1").pack(side=tk.TOP)
        note1 = tk.Listbox(note1frame)
        for note in self.parent.notes:
            note1.insert(tk.END, note)
        note1.bind("<<ListboxSelect>>", self.parent.choose_note1)
        note1.pack(side=tk.LEFT)
        note1scroll = tk.Scrollbar(note1frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y)

        note1frame.pack(side=tk.LEFT)
        note2frame = tk.Frame(self)

        note2label = tk.Label(note2frame, text="Note 2").pack(side=tk.TOP)
        note2 = tk.Listbox(note2frame)

        for note in self.parent.notes:
            note2.insert(tk.END, note)

        note2.bind("<<ListboxSelect>>", self.parent.choose_note2)
        note2.pack(side=tk.LEFT)
        note2scroll = tk.Scrollbar(note2frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y)

        note2frame.pack(side=tk.LEFT)

        self.pack()


class Plot(tk.Frame):
    """
    A frame for storing the plot generated by matplotlib
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background="white")
        self.parent = parent

        T = [float(num)/100.0 for num in range(0, 1001)]
        X = [self.parent.A.get()*np.sin(self.parent.a.get()*t + self.parent.delta.get()) for t in T]
        Y = [self.parent.B.get()*np.sin(self.parent.b.get()*t) for t in T]

        #Create plot
        f = Figure(figsize=(5, 5), dpi=100)
        plot = f.add_subplot(111)
        plot.plot(X, Y)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=4, columnspan=7, rowspan=7, padx=40)

        self.pack()

root = tk.Tk()
root.geometry("800x800")
app = LissajousGenerator(root)
root.mainloop()

# p = pyaudio.PyAudio()
#
# samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
#
# stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs, output=True)
#
# stream.write(volume*samples)
#
# stream.stop_stream()
# stream.close()
#
# p.terminate()
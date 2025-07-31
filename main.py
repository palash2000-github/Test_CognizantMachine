import tkinter as tk
import math
print ("Palash Jaiswal")
name = "Scientific Calculator"
print(name)
b = 10 
b = "Palash"
a = 30
d = 2.001
c = str (a + d) + b
print (c)
class ScientificCalculator:
    def __init__(self, master):
        self.master = master
        master.title("Scientific Calculator")
        master.geometry("400x600")
        master.resizable(False, False)
        master.configure(bg="#2c3e50")

        self.expression = ""
        self.input_text = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Input field
        input_frame = tk.Frame(self.master, width=400, height=100, bd=0, highlightbackground="#34495e", highlightcolor="#34495e", highlightthickness=2)
        input_frame.pack(side=tk.TOP)

        input_field = tk.Entry(input_frame, font=('arial', 18, 'bold'), textvariable=self.input_text, width=50, bg="#ecf0f1", bd=0, justify=tk.RIGHT)
        input_field.grid(row=0, column=0)
        input_field.pack(ipady=10)

        # Buttons frame
        btns_frame = tk.Frame(self.master, width=400, height=500, bg="#2c3e50")
        btns_frame.pack()

        # Row 1: Scientific functions
        self.create_button(btns_frame, "sin", 1, 0, self.scientific_operation)
        self.create_button(btns_frame, "cos", 1, 1, self.scientific_operation)
        self.create_button(btns_frame, "tan", 1, 2, self.scientific_operation)
        self.create_button(btns_frame, "log", 1, 3, self.scientific_operation)
        self.create_button(btns_frame, "sqrt", 1, 4, self.scientific_operation)

        # Row 2: Numbers and operations
        self.create_button(btns_frame, "7", 2, 0, self.btn_click)
        self.create_button
import tkinter as tk
import math
# print ("Palash Jaiswal")
# name = "Scientific Calculator"
# print(name)
# b = 10 
# b = "Palash"
# a = 30
# d = 2.001
# c = str (a + d) + b
# print (c)
# print ("TESTER")
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
        input_frame = tk.Frame(self.master, bd=0, highlightbackground="#34495e", highlightcolor="#34495e", highlightthickness=2)
        input_frame.pack(side=tk.TOP)

        input_field = tk.Entry(input_frame, font=('arial', 24, 'bold'), textvariable=self.input_text, width=24, bg="#ecf0f1", bd=0, justify=tk.RIGHT)
        input_field.grid(row=0, column=0)
        input_field.pack(ipady=20, padx=10, pady=10)

        # Buttons frame
        btns_frame = tk.Frame(self.master, bg="#2c3e50")
        btns_frame.pack(expand=True, fill="both")

        # Button layout
        # Row 1
        self.create_button(btns_frame, "sin", 1, 0, self.scientific_operation)
        self.create_button(btns_frame, "cos", 1, 1, self.scientific_operation)
        self.create_button(btns_frame, "tan", 1, 2, self.scientific_operation)
        self.create_button(btns_frame, "log10", 1, 3, self.scientific_operation)
        self.create_button(btns_frame, "sqrt", 1, 4, self.scientific_operation)

        # Row 2
        self.create_button(btns_frame, "(", 2, 0, self.btn_click)
        self.create_button(btns_frame, ")", 2, 1, self.btn_click)
        self.create_button(btns_frame, "C", 2, 4, self.btn_clear, bg="#c0392b")

        # Row 3
        self.create_button(btns_frame, "7", 3, 0, self.btn_click)
        self.create_button(btns_frame, "8", 3, 1, self.btn_click)
        self.create_button(btns_frame, "9", 3, 2, self.btn_click)
        self.create_button(btns_frame, "/", 3, 3, self.btn_click)

        # Row 4
        self.create_button(btns_frame, "4", 4, 0, self.btn_click)
        self.create_button(btns_frame, "5", 4, 1, self.btn_click)
        self.create_button(btns_frame, "6", 4, 2, self.btn_click)
        self.create_button(btns_frame, "*", 4, 3, self.btn_click)

        # Row 5
        self.create_button(btns_frame, "1", 5, 0, self.btn_click)
        self.create_button(btns_frame, "2", 5, 1, self.btn_click)
        self.create_button(btns_frame, "3", 5, 2, self.btn_click)
        self.create_button(btns_frame, "-", 5, 3, self.btn_click)

        # Row 6
        self.create_button(btns_frame, "0", 6, 0, self.btn_click, colspan=2)
        self.create_button(btns_frame, ".", 6, 2, self.btn_click)
        self.create_button(btns_frame, "+", 6, 3, self.btn_click)
        self.create_button(btns_frame, "=", 4, 4, self.btn_equal, rowspan=3, bg="#27ae60")

        # Configure grid weights for responsiveness
        for i in range(5):
            btns_frame.grid_columnconfigure(i, weight=1)
        for i in range(1, 7):
            btns_frame.grid_rowconfigure(i, weight=1)

    def create_button(self, frame, text, row, col, command, colspan=1, rowspan=1, bg="#34495e", fg="#ecf0f1"):
        action = lambda: command(text) if command in [self.btn_click, self.scientific_operation] else command
        button = tk.Button(frame, text=text, font=('arial', 12, 'bold'), bd=0, bg=bg, fg=fg, command=action)
        button.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan, padx=1, pady=1, sticky="nsew")

    def btn_click(self, item):
        self.expression += str(item)
        self.input_text.set(self.expression)

    def btn_clear(self):
        self.expression = ""
        self.input_text.set("")

    def btn_equal(self):
        try:
            result = str(eval(self.expression))
            self.input_text.set(result)
            self.expression = result
        except Exception:
            self.input_text.set("Error")
            self.expression = ""

    def scientific_operation(self, op):
        self.expression += f"math.{op}("
        self.input_text.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()
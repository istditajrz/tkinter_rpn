#!/bin/python3.10
from __future__ import annotations
import tkinter as tk


from RPN_calc import Calculator


class App(tk.Tk):
    input: tk.StringVar
    output: tk.StringVar
    calculator: Calculator
    entrys: Entrys
    functions: Functions

    def __init__(self) -> None:
        super().__init__()
        self.title("Calculator")
        self.geometry("600x300")
        self.input = tk.StringVar(self)
        self.output = tk.StringVar(self)
        self.calculator = Calculator()
        self.entrys = Entrys(self)
        self.entrys.grid(row=0, column=0, sticky=tk.E + tk.W)
        self.functions = Functions(self)
        self.functions.grid(row=2, column=0, sticky=tk.E + tk.W, padx=5)

    def process_input(self):
        try:
            out = self.calculator.eval_expr(self.input.get())
            self.input.set("")
            if out.startswith("Registered function: "):
                function = out[-1]
                self.functions.register_function(function)
                self.output.set("New " + function)
            else:
                self.output.set(out)
        except ValueError as e:
            self.output.set(e.args[0])

    def update_input(self, text: str):
        def out():
            self.input.set(self.input.get() + text)
            i = self.entrys.in_bar.index(tk.INSERT)
            newi = i + len(text)
            self.entrys.in_bar.icursor(newi)
        return out


class Entrys(tk.Frame):
    master: App
    in_bar: tk.Entry
    enter_b: tk.Button
    out_frame: tk.LabelFrame
    out_bar: tk.Label

    def __init__(self, master: App) -> None:
        self.master = master
        super().__init__(master)

        self.in_bar = tk.Entry(
            self, textvariable=master.input, width=50)
        self.in_bar.bind("<Return>", lambda _: self.master.process_input())
        self.in_bar.grid(row=0, column=0, columnspan=16, padx=5)
        self.in_bar.focus()
        self.enter_b = tk.Button(self, text="⏎", command=master.process_input)
        self.enter_b.grid(row=0, column=17)
        self.out_frame = tk.LabelFrame(self, text="Output", labelanchor="n")
        self.out_frame.grid(row=0, column=18, padx=5)
        self.out_bar = tk.Label(
            self.out_frame, textvariable=self.master.output, justify=tk.CENTER)
        self.out_bar.grid(row=0, column=18)


class Functions(tk.LabelFrame):
    master: App
    func_list: list[tuple[str, tk.Button]]

    def __init__(self, master) -> None:
        self.master = master
        super().__init__(master, labelanchor="nw", text="Functions")
        empty = tk.Button(self, state=tk.DISABLED,
                          text="Empty", relief=tk.FLAT)
        empty.grid(row=2, column=0, pady=2, padx=2)
        self.func_list = [(None, empty)]

    def register_function(self, function: str):
        if self.func_list[0][0] == None:
            self.func_list[0][1].destroy()
            self.func_list.pop(0)
        if function not in map(lambda x: x[0], self.func_list):
            b = tk.Button(self, text=function,
                          command=self.master.update_input(function),
                          relief=tk.RAISED)
            b.grid(row=2, column=len(self.func_list) + 1, padx=2, pady=2)
            self.func_list.append((function, b))


if __name__ == '__main__':
    App().mainloop()

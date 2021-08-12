import pint
import numpy as np
import tkinter as tk
from tkinter import ttk
import json
import sympy
import copy

class Calculator(ttk.Frame):    
    def __init__(self,master):
        ttk.Frame.__init__(self,master)
        self.master = master
        self.master.title("Laser calculator")

        with open('functions.json', 'r') as file:
            self.settings = json.load(file)

        self.ureg = pint.UnitRegistry()

        self.functions = list(self.settings.keys())
        self.functions_names = [self.settings[x]["name"] for x in self.functions]
        functions_names_sorted = copy.deepcopy(self.functions_names)
        functions_names_sorted.sort()
        frame_choose_function = ttk.Frame(self)
        ttk.Label(frame_choose_function,text="Choose a function:").grid(column=0,row=0,sticky="w")
        self.function_selected = tk.StringVar()
        self.function_dropdown = ttk.Combobox(frame_choose_function,textvariable=self.function_selected,width=30)
        self.function_dropdown["values"] = functions_names_sorted
        self.function_dropdown.state(["readonly"])
        self.function_dropdown.grid(row=1,column=0,sticky="ew")
        self.function_dropdown.bind('<<ComboboxSelected>>', self.on_function_selected)
        frame_choose_function.columnconfigure(0,weight=1)
        frame_choose_function.grid(row=0,column=0,sticky="nsew")
        instructions = "Choose a function to calculate or an equation to solve.\nIn calculation, all inputs must be filled. Unceratinty can be added for linear functions by +-.\nWhen solving, the variable for which you solve should be marked by x. "
        self.frame_main = ttk.Frame(self)
        ttk.Label(self.frame_main,text=instructions,wraplength=280,justify="left").grid(row=0,column=0,sticky="ew",columnspan=3)
        self.frame_main.grid(column=0,row=1)

    def on_function_selected(self,event=None):
        try:
            self.frame_main.grid_forget()
            self.frame_main.destroy()
        except:
            pass

        fun = self.functions[self.functions_names.index(self.function_selected.get())]

        self.frame_main = ttk.Frame(self)
        ttk.Label(self.frame_main,text=self.settings[fun]["description"],wraplength=280,justify="left").grid(row=0,column=0,sticky="ew",columnspan=3)
        try:
            self.formula_preview = tk.PhotoImage(file="formulas/{}.png".format(fun))
            ttk.Label(self.frame_main,image=self.formula_preview).grid(row=1,column=0,sticky="ew",columnspan=3)
        except:
            pass
        
        if self.settings[fun]["regime"] == "calc":
            self.build_calc(fun)
        elif self.settings[fun]["regime"] == "solve":
            self.build_solve(fun)
        else:
            self.write("Something is wrong with the definition.")

    def build_solve(self,fun):
        self.var_units = []
        self.var_values = []
        self.var_CB = []
        for ind,name in enumerate(self.settings[fun]["variables"].keys()):
            ttk.Label(self.frame_main,text=self.settings[fun]["variables"][name]["name"]).grid(row=2+ind,column=0,sticky="w")
            self.var_values.append(tk.StringVar(value=0))
            ttk.Entry(self.frame_main,textvariable=self.var_values[ind]).grid(row=2+ind,column=1,sticky="ew")
            self.var_units.append(tk.StringVar())
            try: 
                self.var_units[ind].set(value=self.settings[fun]["variables"][name]["units"][0])
            except:
                pass
            self.var_CB.append(ttk.Combobox(self.frame_main,textvariable=self.var_units[ind],width=10))
            self.var_CB[ind]["values"] = self.settings[fun]["variables"][name]["units"]
            self.var_CB[ind].state(["readonly"])
            self.var_CB[ind].grid(row=2+ind,column=2,sticky="e")
        
        ttk.Button(self.frame_main,text="Solve",command=self.calculate_btn).grid(row=101,column=0,columnspan=3,sticky="ew")
        self.result = tk.StringVar(value="Result")
        self.result_number = tk.StringVar()
        ttk.Label(self.frame_main,textvariable=self.result,font=("Arial", 18),wraplength=280).grid(row=102,column=0,columnspan=3,sticky="ew")
        ttk.Entry(self.frame_main,textvariable=self.result_number).grid(row=103,column=0,columnspan=3,sticky="ew")
        self.frame_main.columnconfigure(1,weight=1)
        self.frame_main.grid(column=0,row=1)


    def build_calc(self,fun):
        self.inputs_units = []
        self.inputs_values = []
        self.inputs_CB = []
        for ind,name in enumerate(self.settings[fun]["inputs"].keys()):
            ttk.Label(self.frame_main,text=name).grid(row=2+ind,column=0,sticky="w")
            self.inputs_values.append(tk.StringVar(value=0))
            ttk.Entry(self.frame_main,textvariable=self.inputs_values[ind]).grid(row=2+ind,column=1,sticky="ew")
            self.inputs_units.append(tk.StringVar())
            try: 
                self.inputs_units[ind].set(value=self.settings[fun]["inputs"][name]["units"][0])
            except:
                pass
            self.inputs_CB.append(ttk.Combobox(self.frame_main,textvariable=self.inputs_units[ind],width=10))
            self.inputs_CB[ind]["values"] = self.settings[fun]["inputs"][name]["units"]
            self.inputs_CB[ind].state(["readonly"])
            self.inputs_CB[ind].grid(row=2+ind,column=2,sticky="e")
        
        ttk.Label(self.frame_main,text=f"Units of output ({self.settings[fun]['outputs']['name']})").grid(row=100,column=0,sticky="ew",columnspan=2)
        self.output = tk.StringVar()        
        try:
            self.output.set(value=self.settings[fun]["outputs"]["units"][0])
        except:
            pass
        self.output_CB = ttk.Combobox(self.frame_main,textvariable=self.output,width=10)
        self.output_CB["values"] = self.settings[fun]["outputs"]["units"]
        self.output_CB.state(["readonly"])
        self.output_CB.grid(row=100,column=2,sticky="e")

        ttk.Button(self.frame_main,text="Calculate",command=self.calculate_btn).grid(row=101,column=0,columnspan=3,sticky="ew")
        self.result = tk.StringVar(value="Result")
        self.result_number = tk.StringVar()
        ttk.Label(self.frame_main,textvariable=self.result,font=("Arial", 18),wraplength=280).grid(row=102,column=0,columnspan=3,sticky="ew")
        ttk.Entry(self.frame_main,textvariable=self.result_number).grid(row=103,column=0,columnspan=3,sticky="ew")
        self.frame_main.columnconfigure(1,weight=1)
        self.frame_main.grid(column=0,row=1)

    def calculate_btn(self):
        fun = self.functions[self.functions_names.index(self.function_selected.get())]
        if self.settings[fun]["regime"] == "calc":
            self.calculate(fun)
        elif self.settings[fun]["regime"] == "solve":
            self.solve(fun)
        else:
            self.write("Something is wrong with the definition.")
    
    def solve(self,fun):
        found_x = False
        I = [None] * len(self.var_values)
        str_to_eval = [None] * len(self.var_values)
        # Deciding, what to solve
        for ind,name in enumerate(self.settings[fun]["variables"].keys()):
            I[ind] = sympy.symbols(name)
            if self.var_values[ind].get().strip() == "x":
                if found_x == False:
                    x = I[ind]
                    resulting_units = self.var_units[ind].get()
                    resulting_name = self.settings[fun]["variables"][name]["name"]
                    found_x = True
                else:
                    self.write("Too many x's.")
                    return 0
            else:
                str_to_eval[ind] = "{0} = float(self.var_values[{1}].get().replace(',','.')) * self.ureg(self.var_units[{1}].get())".format(name,ind)
        if not found_x:
            self.write("One x required.")
            return 0
        solution = sympy.solve(eval(self.settings[fun]["function"]),x)
        solution = str(solution[0])
        # Creating variables for the solution
        for string in str_to_eval:
            try: 
                if string is not None:
                    exec(string)
            except ValueError:
                self.write("Cannot convert to numbers!")
                return 0
        # Solving
        try:
            result = eval(solution).to(resulting_units)
            self.result.set(value="{} is {:.3fP}".format(resulting_name,result))
            self.result_number.set(value=str(result.magnitude))
        except ZeroDivisionError:
            self.write("Cannot divide by zero!")
            return 0


    def calculate(self,fun):
        I = [None] * len(self.inputs_values)
        for ind,name in enumerate(self.settings[fun]["inputs"].keys()):
            value = self.inputs_values[ind].get().replace(",",".")
            try:
                value = value.split("+-")
                magnitude = value[0].strip()
                if len(value) > 1:
                    error = value[1].strip()     
                    I[self.settings[fun]["inputs"][name]["position"]] = (float(magnitude) * self.ureg(self.inputs_units[ind].get())).plus_minus(float(error)) 
                else:
                    error = 0           
                    I[self.settings[fun]["inputs"][name]["position"]] = (float(magnitude) * self.ureg(self.inputs_units[ind].get())) 
            except ValueError:
                self.write("Cannot convert to numbers!")
                return 0
        function_to_evaluate = self.settings[fun]["function"]        
        try:
            result = eval(function_to_evaluate).to(self.output.get())
            self.result.set(value="{} is {:.3fP}".format(self.settings[fun]['outputs']['name'],result))
            self.result_number.set(value=str(result.magnitude))
        except ZeroDivisionError:
            self.write("Cannot divide by zero!")
            return 0
        except TypeError:
            self.write("Uncertainties not implemented for nonlinear functions.")
            return 0

    def write(self,message="Result"):
        self.result.set(value=str(message))
        self.result_number.set(value=str(message))

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    app.grid(column=0,row=0)
    root.mainloop()
    
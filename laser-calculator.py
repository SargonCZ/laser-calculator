import pint
import numpy as np
import tkinter as tk
from tkinter import ttk
import json
import sympy
import copy
import datetime

class Calculator(ttk.Frame):    
    def __init__(self,master):
        ttk.Frame.__init__(self,master)
        self.master = master
        self.master.title("Laser calculator")
        self.master.option_add("*tearOff", tk.FALSE)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)      

        with open('functions.json', 'r') as file:
            self.settings = json.load(file)
        with open("constants.json","r") as file:
            self.constants = json.load(file)
        try:
            with open('history.json', 'r') as file:
                self.history = json.load(file)
        except FileNotFoundError:
            self.history = dict()

        self.ureg = pint.UnitRegistry()

        self.p_history = tk.PhotoImage(master=self,file=r"icons/log.png")
        self.p_clear = tk.PhotoImage(master=self,file=r"icons/delete.png")
        self.p_calc = tk.PhotoImage(master=self,file=r"icons/calc.png")

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
        instructions = "Choose a function to calculate or an equation to solve.\nIn calculation, all inputs must be filled.\nWhen solving, the variable for which you solve should be marked by x.\nUnceratinty can be added for linear functions by +-."
        self.frame_main = ttk.Frame(self)
        ttk.Label(self.frame_main,text=instructions,wraplength=280,justify="left").grid(row=0,column=0,sticky="ew",columnspan=3)
        self.frame_main.grid(column=0,row=1)

        self.menubar = tk.Menu(self.master)
        self.master["menu"] = self.menubar
        self.menu_options = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_options,label="Options")
        self.menu_options.add_command(label="Show history",command=self.show_history,image=self.p_history,compound=tk.LEFT,accelerator="Ctrl+H")
        self.menu_options.add_command(label="Clear history",command=self.clear_history,image=self.p_clear,compound=tk.LEFT)
        self.history_window_open = False

        self.bind_all("<Control-KeyPress-h>",self.show_history)

    def on_closing(self):
        with open('history.json', 'w') as file:
            json.dump(self.history,file,sort_keys=True, indent=4)
        self.master.destroy()

    def show_history(self,event=None):
        try:
            self.history_window.destroy()
            self.history_window_open = False
        except:
            pass
        self.history_window = tk.Toplevel(self.master)
        self.history_window.title("History")
        self.history_window.protocol("WM_DELETE_WINDOW", self.close_history)        
        
        self.history_tree = ttk.Treeview(self.history_window,columns=("function","inputs","outputs"))
        self.history_tree.heading("#0",text="Time")
        self.history_tree.heading("function",text="Function")
        self.history_tree.heading("inputs",text="Inputs")
        self.history_tree.heading("outputs",text="Output")
        self.history_tree.column("#0",stretch=False,width=150)
        self.history_tree.column("function",stretch=False,width=200)
        self.history_tree.column("inputs",stretch=True,width=350)
        self.history_tree.column("outputs",stretch=True,width=350)        
        self.history_tree.grid(column=1,row=1,sticky="nsew")
        scrlbar = ttk.Scrollbar(self.history_window,command=self.history_tree.yview)
        self.history_tree.config(yscrollcommand = scrlbar.set)
        scrlbar.grid(column=2,row=1,sticky="nsew")
        self.history_window.columnconfigure(1,weight=1)
        self.history_window.rowconfigure(1,weight=1)
        self.history_window_open = True
        for key in self.history.keys():
            self.history_tree.insert("",0,text=key,values=self.history[key])
    
    def close_history(self):
        self.history_window_open = False
        self.history_window.destroy()

    def add_history(self,what=()):
        now = datetime.datetime.now().isoformat(sep=" ",timespec="seconds")
        self.history[str(now)] = what 
        if self.history_window_open:
            self.history_tree.insert("",0,text=now,values=what)

    def clear_history(self):
        self.history = dict()
        if self.history_window_open:
            for children in self.history_tree.get_children():
                self.history_tree.delete(children)

    def on_function_selected(self,event=None):
        '''Called, when a function is selected
        Will clear the GUI of the controlling elements of the last function
        and will build a new one. Depending on the calculation regime, 
        it will call either build_calc or build_solve function. Finally,
        it will create a view for the constants.
        '''
        try:
            self.frame_main.grid_forget()            
            self.frame_main.destroy()
        except:
            pass
        try:
            self.frame_tree.grid_forget()
            self.frame_tree.destroy()
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

        # if constants, adding list of them
        const = self.settings[fun].get("constants",None)
        if const:
            self.frame_tree = ttk.Frame(self)
            tree = ttk.Treeview(self.frame_tree,columns=("name","value"))
            tree.heading("#0",text="Constant")
            tree.heading("name",text="Name")
            tree.heading("value",text="Value")
            tree.column('#0', width=70, anchor='w')
            tree.column('name', width=140, anchor='w')
            tree.column('value', width=110, anchor='e')
            for name in const:
                tree.insert('','end',name,text=name)
                tree.item(name,open=tk.TRUE)
                for vals in self.constants[name].keys():
                    tree.insert(name,'end',vals,values=(vals,self.constants[name][vals]))
            tree.grid(column=1,row=1,sticky="nsew")
            scrlbar = ttk.Scrollbar(self.frame_tree,command=tree.yview)
            tree.config(yscrollcommand = scrlbar.set)
            scrlbar.grid(column=2,row=1,sticky="nsew")
            self.frame_tree.grid(column=1,row=0,rowspan=2,sticky="nsew")
            self.frame_tree.rowconfigure(1,weight=1)
            

    def build_solve(self,fun):
        self.var_units = []
        self.var_values = []
        self.var_CB = []
        for ind,name in enumerate(self.settings[fun]["variables"].keys()):
            uneditable = False
            ttk.Label(self.frame_main,text=self.settings[fun]["variables"][name]["name"]).grid(row=2+ind,column=0,sticky="w")
            try:
                self.var_values.append(tk.StringVar(value=self.settings[fun]["variables"][name]["value"]))
                uneditable = True
            except KeyError:
                self.var_values.append(tk.StringVar(value=0))
            current_Entry = ttk.Entry(self.frame_main,textvariable=self.var_values[ind])
            if uneditable:
                current_Entry.config(state="disabled")
            current_Entry.grid(row=2+ind,column=1,sticky="ew")
            self.var_units.append(tk.StringVar())
            try: 
                self.var_units[ind].set(value=self.settings[fun]["variables"][name]["units"][0])
            except:
                pass
            self.var_CB.append(ttk.Combobox(self.frame_main,textvariable=self.var_units[ind],width=10))
            self.var_CB[ind]["values"] = self.settings[fun]["variables"][name]["units"]
            if uneditable:
                self.var_CB[ind].state(["disabled"])
            else:
                self.var_CB[ind].state(["readonly"])
            self.var_CB[ind].grid(row=2+ind,column=2,sticky="e")
        
        ttk.Button(self.frame_main,text="Solve",command=self.calculate_btn,image=self.p_calc,compound=tk.LEFT).grid(row=101,column=0,columnspan=3,sticky="ew")
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

        ttk.Button(self.frame_main,text="Calculate",command=self.calculate_btn,image=self.p_calc,compound=tk.LEFT).grid(row=101,column=0,columnspan=3,sticky="ew")
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
        inputs = ""
        # Deciding, what to solve
        for ind,name in enumerate(self.settings[fun]["variables"].keys()):
            I[ind] = sympy.symbols(name)
            value = self.var_values[ind].get().strip().replace(",",".")
            if value == "x":
                if found_x == False:
                    x = I[ind]
                    resulting_units = self.var_units[ind].get()
                    resulting_name = self.settings[fun]["variables"][name]["name"]
                    found_x = True
                else:
                    self.write("Too many x's.")
                    return 0
            else:
                value = value.split("+-")
                magnitude = value[0].strip()
                if len(value) > 1:
                    error = value[1].strip()
                    str_to_eval[ind] = "{} = (float({}) * self.ureg(self.var_units[{}].get())).plus_minus(float({}))".format(name,magnitude,ind,error)
                else:
                    str_to_eval[ind] = "{} = float({}) * self.ureg(self.var_units[{}].get())".format(name,magnitude,ind)
                inputs = inputs + f"{self.settings[fun]['variables'][name]['name']} = {self.var_values[ind].get().replace(',','.')} {self.var_units[ind].get()}, "
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
            self.add_history((self.settings[fun]["name"],inputs[0:-2],f"{resulting_name} = {str(result)}"))
        except ZeroDivisionError:
            self.write("Cannot divide by zero!")
            return 0


    def calculate(self,fun):
        I = [None] * len(self.inputs_values)
        inputs = ""
        for ind,name in enumerate(self.settings[fun]["inputs"].keys()):
            value = self.inputs_values[ind].get().replace(",",".")
            try:
                value = value.split("+-")
                magnitude = value[0].strip()
                if len(value) > 1:
                    error = value[1].strip()     
                    I[self.settings[fun]["inputs"][name]["position"]] = (float(magnitude) * self.ureg(self.inputs_units[ind].get())).plus_minus(float(error)) 
                else:                            
                    I[self.settings[fun]["inputs"][name]["position"]] = (float(magnitude) * self.ureg(self.inputs_units[ind].get())) 
                inputs = inputs + f"{name} = {self.inputs_values[ind].get().replace(',','.')} {self.inputs_units[ind].get()}, "
            except ValueError:
                self.write("Cannot convert to numbers!")
                return 0
        function_to_evaluate = self.settings[fun]["function"]        
        try:
            result = eval(function_to_evaluate).to(self.output.get())
            self.result.set(value="{} is {:.3fP}".format(self.settings[fun]['outputs']['name'],result))
            self.result_number.set(value=str(result.magnitude))
            self.add_history((self.settings[fun]["name"],inputs[0:-2],f"{self.settings[fun]['outputs']['name']} = {str(result)}"))
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
    
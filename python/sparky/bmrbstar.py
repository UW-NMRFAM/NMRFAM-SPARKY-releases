import sparky
import tkutil
import sputil
import Tkinter
import tkFileDialog
import starlib
import os
import tkMessageBox
class Test_dialog(tkutil.Dialog):
    def __init__(self, session):
        self.session = session

        tkutil.Dialog.__init__(self, self.session.tk, 'Load BMRB STAR File')
        self.molecule = Tkinter.StringVar()
        self.condition = Tkinter.StringVar()
        condition = sputil.selected_condition(self.session)
        self.str_file = None
        self.create_ui()
        self.resonances = None

    def create_ui(self):
        top_row = Tkinter.Frame(self.top)
        open_button = Tkinter.Button(top_row, text = "Open...", command = self.open_cb)
        open_button.pack(side = 'left', anchor = 'w')
        cm = sputil.condition_menu(self.session, top_row, "Condition:")
        cm.frame.pack(side = 'top', anchor = 'w')
        self.condition_menu = cm
        top_row.pack(side = 'top', anchor = 'w')

        preview_heading = "%4s %10s %8s %8s %10s" %("Load", "Group", "Atom", "Nuclei", "Shift")

        self.preview = tkutil.scrolling_list(self.top, heading = preview_heading, height = 16)
        self.preview.listbox['width']= 55
        self.preview.listbox.config(selectmode = Tkinter.EXTENDED)
        self.preview.listbox.bind("<Double-Button-1>", self.double_click_cb)
        self.preview.frame.pack(side = 'top', anchor = 'w', fill = 'both', expand = 1)

        bot_row = Tkinter.Frame(self.top)
        self.sort_but = Tkinter.Menubutton(bot_row, text = "Sort By", relief = Tkinter.RAISED)
        self.sort_but.menu = Tkinter.Menu(self.sort_but, tearoff = 0)
        self.sort_but.menu.add_command(label = "[X] Group", command = self.group_sort_cb)
        self.sort_but.menu.add_command(label = "[ ] Atom", command = self.atom_sort_cb)
        self.sort_but.menu.add_command(label = "[ ] Chemical Shift", command = self.cs_sort_cb)
        self.sort_but["menu"] = self.sort_but.menu
        self.sort_but.pack(side = 'left', anchor = 'w', fill = Tkinter.Y)
        br = tkutil.button_row(bot_row, 
                               ("Select", self.select_cb),
                               ("Unselect", self.unselect_cb),
                               ("Load", self.load_cb),
                               ("Close", self.close_cb),
                               ("Help", sputil.help_cb(self.session, "LoadBMRB"))
                               )
        br.frame.pack(side = 'left', anchor = 'w')
        bot_row.pack(side = 'top', anchor = 'w')

    def update_sort_menu(self, sort_method):
        if sort_method == "group":
            select = ["[X] Group", "[ ] Atom", "[ ] Chemical Shift"]
        elif sort_method == "atom":
            select = ["[ ] Group", "[X] Atom", "[ ] Chemical Shift"]
        else:
            select = ["[ ] Group", "[ ] Atom", "[X] Chemical Shift"]
        for i in range(3):
            self.sort_but.menu.entryconfig(i, label = select[i])

    def group_sort_cb(self):
        self.update_sort_menu("group")
        self.resonances.sort(key = lambda x: x.atom_index)
        self.update_preview()

    def atom_sort_cb(self):
        self.update_sort_menu("atom")
        self.resonances.sort(key = lambda x: x.atom)
        self.update_preview()

    def cs_sort_cb(self):
        self.update_sort_menu("cs")
        self.resonances.sort(key = lambda x: x.shift)
        self.update_preview()
    
    def open_cb(self):
        try:
            self.str_file = tkFileDialog.askopenfilename(initialdir = os.environ["SPARKYHOME"])
        except KeyError:
            self.str_file = tkFileDialog.askopenfilename()
        try:
            self.resonances = starlib.load_file(self.str_file)
        except ValueError:
            tkMessageBox.showwarning("Error", "Invalid file type or corrupted file")
            return
        except IOError:
            self.str_file = None
            return
        if len(self.resonances) == 0:
            tkMessageBox.showwarning("Error", "No resonances found in the file")
            return
        self.update_preview()


    def update_preview(self):
        self.preview.clear()
        for res in self.resonances:
            self.preview.append(str(res))

    def select_cb(self):
        indice = self.preview.selected_line_numbers()
        for index in indice:
            res = self.resonances[index]
            res.load = True 
            self.preview.listbox.delete(index)
            self.preview.listbox.insert(index, str(res))

    def unselect_cb(self):
        indice = self.preview.selected_line_numbers()
        for index in indice:
            res = self.resonances[index]
            res.load = False 
            self.preview.listbox.delete(index)
            self.preview.listbox.insert(index, str(res))

    def double_click_cb(self, event):
        try:
            index = self.preview.selected_line_numbers()[0]
        except IndexError:
            return
        res = self.resonances[index]
        res.load = not res.load 
        self.preview.listbox.delete(index)
        self.preview.listbox.insert(index, str(res))
        
    def load_cb(self):
        if self.str_file == None:
            tkMessageBox.showwarning("Error", "No BMRB file opened")
            return
        condition = self.condition_menu.condition()

        for res in self.resonances:
            condition.add_resonance(res.group, res.atom, res.nuclei, res.shift)
        self.session.selected_spectrum().needs_save = True

def show_dialog(session):
    d = sputil.the_dialog(Test_dialog, session)
    d.show_window(1)

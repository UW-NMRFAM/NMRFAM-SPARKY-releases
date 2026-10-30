import sparky
import tkutil
import sputil
import Tkinter
import tkFileDialog
import selectorlib
import os
import tkMessageBox
import peaklist

class Test_dialog(tkutil.Dialog):
    def __init__(self, session):
        self.session = session
        tkutil.Dialog.__init__(self, self.session.tk, 'Advanced Selection- from Rienstra group (UW-Madison)')
        self.spectrum = session.selected_spectrum()
        self.dim = self.spectrum.dimension
        self.entries = []
        self.status = Tkinter.StringVar()
        self.create_ui()

    def create_ui(self):
        for i in range(self.dim):
            entry_frame = Tkinter.Frame(self.top)
            label = Tkinter.Label(entry_frame, text = "w%d: "%(i+1))
            label.pack(side = "left")
            entry = Tkinter.Entry(entry_frame, width = 60)
            entry.pack(side = "left")
            self.entries.append(entry)
            entry_frame.pack(side = "top", anchor = "w")
        lb = Tkinter.Label(self.top, textvariable = self.status, relief = Tkinter.SUNKEN, width = 64, anchor = Tkinter.W)
        lb.pack(side = 'top', anchor = 'w')
        self.status.set("Ready to select peaks.")
        br = tkutil.button_row(self.top, 
                               ("Select", self.select_cb),
                               ("Unselect", self.unselect_cb),
                               ("Peak List", self.show_list_cb),
                               ("Cheat Sheet", self.cheat_sheet_cb),
                               ("Close", self.but_close_cb),
                               #("Help", sputil.help_cb(self.session, "LoadBMRB"))
                               )
        br.frame.pack(side = 'top', anchor = 'w')
    def show_list_cb(self):
        peaklist.show_selected_peaks(self.session)

    def select_cb(self):
        self.session.unselect_all_ornaments()
        self.status.set("0 peaks selected.")
        try:
            self.match_and_select()
        except selectorlib.Selection_Error as e:
            tkMessageBox.showwarning("Error", e.parameter)
            self.session.unselect_all_ornaments()
            self.status.set("0 peaks selected.")

    def match_and_select(self):
        expressions = []
        n_peaks = 0
        for entry in self.entries:
            expressions.append(entry.get())
        for peak in self.spectrum.peak_list():
            willSelect = True
            for i, res in enumerate(peak.resonances()):
                matcher = selectorlib.Match(res, peak)
                willSelect = willSelect and matcher.evaluate(expressions[i])
            if willSelect:
                peak.selected = 1 
                n_peaks += 1
        self.status.set("%d peaks selected." %n_peaks)
    def unselect_cb(self):
        self.session.unselect_all_ornaments()
        self.status.set("0 peaks selected.")

    def but_close_cb(self):
        self.close_cb()
        self.top.destroy()

    def cheat_sheet_cb(self):
        cheat_d = sputil.the_dialog(CheatSheet_dialog, self.session)
        cheat_d.show_window(1)

class CheatSheet_dialog(tkutil.Dialog):
    def __init__(self, session):
        self.session = session
        tkutil.Dialog.__init__(self, self.session.tk, 'Peak Selection Cheat Sheet')
        self.create_ui()

    def create_ui(self):
        info_str = \
"""\
Peak Specific Keywords and arguments:
    color      : list of color such as light_blue red
    integrated : no argument 
    height_max : number such as 9e10
    height_min : number such as 9e10
    range_max  : number such as 3 
    range_min  : number such as 3
    volume_max : number such as 1.0e10
    volume_min : number such as 1.0e10

Dimension Specific Keywords and arguments:
    assigned   : no argument or list of ATOM RESID RESIDUE
    backbone   : no argument
    name       : list of atom type such as N CX
    resid      : list of residue number such as 5 6 7 8
                 or a range of number such as 5 to 8
    resname    : list of residue type such as ala phe asp
    sidechain  : no argument

"""

#For more information, see:
#    https://snowchow.scs.uiuc.edu/wiki/index.php/Sparky_advanced_peak_selection
    
        w = Tkinter.Message(self.top, text = info_str, font = "fixedWidthFont", aspect = 180)
        w.pack()


def select(spectrum, expressions):
    spectrum.session.unselect_all_ornaments()
    peaks = []
    for peak in spectrum.peak_list():
        willSelect = True
        for i, res in enumerate(peak.resonances()):
            matcher = selectorlib.Match(res, peak)
            willSelect = willSelect and matcher.evaluate(expressions[i])
        if willSelect:
            peaks.append(peak)
    return peaks


def show_dialog(session):
    try:
        d = sputil.the_dialog(Test_dialog, session)
        d.show_window(1)
    except AttributeError:
        tkMessageBox.showwarning("Error", "Open a spectrum first.")



## Below is for short-cut selection
def select_all_float_labels(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pLabel in spectrum.label_list():
    if pLabel.peak != None:
      pLabel.selected = 0
    else:
      pLabel.selected = 1
        
def select_all_attached_labels(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pLabel in spectrum.label_list():
    if pLabel.peak == None:
      continue
    else:
      pLabel.selected = 1

def select_all_ornaments(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.peak_list():
    pOrmt.selected = 1
  for pOrmt in spectrum.label_list():
    pOrmt.selected = 1
  for pOrmt in spectrum.line_list():
    pOrmt.selected = 1
  for pOrmt in spectrum.grid_list():
    pOrmt.selected = 1

def select_all_grids(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.grid_list():
    pOrmt.selected = 1

def select_all_lines(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.line_list():
    pOrmt.selected = 1
    
def select_all_assigned_peaks(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.peak_list():
    if pOrmt.is_assigned == 1:
      pOrmt.selected = 1
      if pOrmt.label != None:
        pOrmt.label.selected = 1

def select_all_unassigned_peaks(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.peak_list():
    if pOrmt.is_assigned == 0:
      pOrmt.selected = 1

def select_all_userlabeled_peaks(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.peak_list():
    if pOrmt.label != None:
      if pOrmt.label.shows_assignment == 0: # user label
        pOrmt.selected = 1
        pOrmt.label.selected = 1

def select_all_nonuserlabeled_peaks(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.peak_list():
    if pOrmt.label == None:
      pOrmt.selected = 1
    elif pOrmt.label.shows_assignment == 1: # assignment
      pOrmt.selected = 1
      pOrmt.label.selected = 1
      
def select_unconfirmed(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  nselect = 0
  for peak in spectrum.peak_list():
    if peak == None: continue
    peak.selected = 0
    if peak.is_assigned == 0:
      continue
    aslb = peak.assignment
    sp = aslb.strip().split('-')
    for lb in sp:
      if len(lb) > 3:
        if lb[-2:] == '_s':
          peak.selected = 1
          nselect += 1
  session.report_information('\n%d peak(s) selected.\n' % (nselect))
def unselect_all_peaks(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.selected_peaks():
    pOrmt.selected = 1

def select_labels_of_selected_peaks(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  for pOrmt in spectrum.selected_peaks():
    if pOrmt.label != None:
      pOrmt.label.selected = 1

def remove_unnecessary_duplicates(session):
  spectrum = session.selected_spectrum()
  if spectrum == None:
    return
  if len(spectrum.selected_peaks()) == 0:
    peaks = spectrum.peak_list()
  else:
    peaks = spectrum.selected_peaks()
  num_among = len(peaks)
  # check uniqueness
  keep_list=[]
  for i in range(len(peaks)):
    peak = peaks[i]
    peak.selected = 0
    if peak.label != None:
      peak.label.selected = 0
    bKeep = True
    for j in range(len(keep_list)):
      peak2 = keep_list[j]
      if peak.frequency != peak2.frequency: continue
      if peak.is_assigned == 0 and peak2.is_assigned == 0:
        bKeep = False
        break
      if peak.is_assigned == 1 and peak2.is_assigned == 1 and \
          peak.assignment == peak2.assignment:
        bKeep = False
        break
    if bKeep:
      keep_list.append(peak)
  num_remove = num_among - len(keep_list)
  # remove unkeep
  for i in range(len(peaks)):
    if peaks[i] not in keep_list:
      peaks[i].selected = 1
  session.command_characters("")
  tkMessageBox.showinfo("Delete duplicates", 
    "%d peaks removed from %d peaks." % (num_remove, num_among))
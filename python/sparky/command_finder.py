# -----------------------------------------------------------------------------
# COMMAND FINDER
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: December 4, 2020
# 
# Find NMRFAM-SPARKY command by a simple search
#
# -----------------------------------------------------------------------------
# CITATION: TBA
#
# -----------------------------------------------------------------------------

import Tkinter

import sparky
import sputil
import tkutil
import tkMessageBox

class commandfind_dialog(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'Command finder')
    keyword_ef = tkutil.entry_field(self.top, 'Search for: ', 
                                    initial = '', width = 10)
    keyword_ef.frame.pack(side = 'top', anchor = 'nw', expand = 0)
    keyword_ef.entry.bind('<Key>', self.update_search_cb)
    self.keyword = keyword_ef.variable

    self.resultbox = tkutil.scrolling_list(self.top, \
                  'Search results', 5, xscrollbar=True)
    self.resultbox.listbox.bind('<Double-Button-1>', self.submit_command_cb)
    self.resultbox.frame.pack(side='top', fill = 'both', expand = 1)
    fo = tkutil.tk_call(session.tk, '.menuBar.fileMenuButton', 'cget', '-font')
    self.resultbox.listbox['font'] = fo
    self.resultbox.heading['font'] = fo

    self.notice_text = Tkinter.StringVar()
    self.notice_text.set("* Dbl-click to launch the command.")
    self.notice = Tkinter.Label(self.top, \
                                textvariable = self.notice_text, 
                                anchor = 'w', justify = 'left')
    self.notice.pack(side = 'bottom', anchor = 'w')
    self.command_list = []
    self.make_command_list()
    self.update_search_cb(None)

  def make_command_list(self):
    s = self.session
    w_list = list(tkutil.tk_call(s.tk, 'winfo', 'children', '.'))
    for item in w_list:
      w_list2 = list(tkutil.tk_call(s.tk, 'winfo', 'children', str(item)))
      w_list.extend(w_list2)

    command_list = []
    label_list = []
    for w in w_list:
      if str(w).find('.menuBar') == -1: continue
      try:
        last_index = tkutil.tk_call(s.tk, str(w), 'index', 'end')
        for i in range(last_index+1):
          try:
            acc = tkutil.tk_call(s.tk, str(w), 'entrycget', str(i), '-accelerator')
            lbl = tkutil.tk_call(s.tk, str(w), 'entrycget', str(i), '-label')
            if acc == None or acc == '': continue
            if lbl[0] == '>': continue
            if lbl + '   [' + acc + ']' in label_list: continue
            command_list.append([lbl + '   [' + acc + ']', acc, lbl])
            label_list.append(lbl + '   [' + acc + ']')
          except:
            continue
      except:
        continue
    sort_list = sorted(command_list, key=lambda x: x[0])
    self.command_list = sort_list

  def update_search_cb(self, event):
    keyword = self.keyword.get()
    self.resultbox.clear()
    for line, cmd, desc in self.command_list:
      if len(keyword) < 2:
        self.resultbox.append(line, [line, cmd, desc])
        continue
      if line.upper().find(keyword.upper()) != -1:
        self.resultbox.append(line, [line, cmd, desc])

  def submit_command_cb(self, event):
    data_list = self.resultbox.selected_line_data()
    if len(data_list) == 0: return
    cmd = data_list[0][1] # line, command, desc
    self.session.command_characters(cmd)

def show_commandfind_dialog(session):
  sputil.the_dialog(commandfind_dialog, session).show_window(1)
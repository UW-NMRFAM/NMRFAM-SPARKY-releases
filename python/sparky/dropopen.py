# -----------------------------------------------------------------------------
# Mutiple spectra to open
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Sep 1, 2015
# 
#
#
# -----------------------------------------------------------------------------

import Tkinter

import sparky
import tkutil
import sputil
import tkMessageBox

# -----------------------------------------------------------------------------
#
class drop_open_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
  
    self.session = session
    
    tkutil.Dialog.__init__(self, session.tk, "Paste files in the clipboard to open all at once")
    
    t = Tkinter.Label(self.top, text = "Select'n copy multiple files in the finder and click Append...", anchor='nw', justify="center")
    t.pack()
    
    self.listbox = tkutil.scrolling_list(self.top, 'List of files', 10)
    self.listbox.frame.pack(side = 'top', fill = 'both', expand = 1)
    
    self.listbox.listbox.bind('<KeyPress-Delete>', self.listbox.delete_selected_cb)
    
    br = tkutil.button_row(self.top,
         ('Append', self.append_cb),
         ('Delete', self.delete_cb),
         ('Clear', self.clear_cb),         
         ('Open', self.open_cb),         
			   ('Close', self.close_cb),
			   )
    br.frame.pack(side = 'top', anchor = 'center')  

    
  def append_cb(self):
    session = self.session
    
    try:
      files = session.tk.selection_get(selection='CLIPBOARD').split()
    except:
      tkMessageBox.showinfo('Unsupported platform..', 'Unfortunately, your system does not support this feature.')
      return
    
    for filename2 in files:
      # check if the file is already in
      filename = filename2.strip('\r\n')
      
      if filename in self.listbox.line_data:
        continue
      # check if already opened   
      iFound = 0
      if session.project != None:
        for spec in session.project.spectrum_list():
          if filename == spec.data_path or filename == spec.save_path:
            iFound = 1
            break
      if iFound == 1: continue
      
      self.listbox.append( filename, filename )
      
  def delete_cb(self):
    slines = self.listbox.selected_line_numbers()
    slines.sort()
    slines.reverse()
    for line_number in slines:
      del self.listbox.line_data[line_number]
      self.listbox.listbox.delete(line_number)

  def open_cb(self):
    session = self.session  
    bad_paths = []
    for path in self.listbox.line_data:
      if self.session.open_spectrum(path) == None:
        bad_paths.append(path)

    if bad_paths:
      message = 'Could not open files:'
      for path in bad_paths:
        message = message + '\n' + path
    else:
      message = 'Opened %d spectra' % len(self.listbox.line_data)

    tkMessageBox.showinfo('Open multi', message)

  def clear_cb(self):
    self.listbox.clear()


# -----------------------------------------------------------------------------
#
def drop_open(session):
  sputil.the_dialog(drop_open_dialog,session).show_window(1)

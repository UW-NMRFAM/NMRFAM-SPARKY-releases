# -----------------------------------------------------------------------------
# Nucleic acid support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Dec 8, 2014
# 
#
# Usage:
#   type "SE" command or select from extension menu
# 
# -----------------------------------------------------------------------------
import math
import string
import types
import Tkinter

import atoms
import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import tkFileDialog
import rna_ellipse

# -----------------------------------------------------------------------------
#
class rna_ellipse_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):
    self.selected_spec_type = None
    
    tkutil.Dialog.__init__(self, session.tk, 'RNA Statistical Ellipses')

    spec = sputil.spectrum_menu(session, self.top, 'Spectrum: ')
    spec.frame.pack(side = 'top', anchor = 'w')
    self.spec = spec
        
    supported_spectra = 'C8H8 H5H6 H6H5'
    self.supported_spectra = supported_spectra;
    supported_spectrum_list = supported_spectra.split()
    self.supported_spectrum_list = supported_spectrum_list
    
    self.type_om = tkutil.option_menu(self.top, "type: ", supported_spectrum_list, 'C8H8')
    self.type_om.frame.pack(side = 'top', anchor = 'nw')
    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top')    

    
    label = Tkinter.Label(self.top, text = "GX -> red", fg="red", bg="black")
    label.pack(side = 'top', fill='both')
    
    label2 = Tkinter.Label(self.top, text = "UX -> cyan", fg="cyan", bg="black")
    label2.pack(side = 'top', fill='both')

    label3 = Tkinter.Label(self.top, text = "CX -> blue", fg="blue", bg="black")
    label3.pack(side = 'top', fill='both')    
        
    label4 = Tkinter.Label(self.top, text = "AX -> green", fg="green", bg="black")
    label4.pack(side = 'top', fill='both')    
    
    label5 = Tkinter.Label(self.top, text = "5',3' -> purple", fg="purple", bg="black")
    label5.pack(side = 'top', fill='both')
    
    sep2 = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep2.pack(fill="both", padx=5,pady=5, side = 'top')  
        
    self.br = tkutil.button_row(self.top,
			   ('Generate Ellipses', self.generate_cb),
			   ('Select Ellipses', self.select_cb),
	   	   ('Close', self.close_cb),
			   )
			   
    self.br.frame.pack(side = 'top', anchor = 'w')
  def select_cb(self):
    if self.spec == None or self.spec.spectrum() == None:
      tkMessageBox.showinfo('Select spectrum','Please select a spectrum.')
      return
    for ln in self.spec.spectrum().line_list():
      ln.selected = 1    
  def generate_cb(self):
    if self.spec == None or self.spec.spectrum() == None:
      tkMessageBox.showinfo('Select spectrum','Please select a spectrum.')
      return
    selected_type = self.type_om.get()
    peak_types = rna_ellipse.rna_ellipse_types[selected_type]
    
    iFliped = 0
    if self.spec.spectrum().nuclei[1] == '13C':
      iFliped = 1
    # loop peak_types
    for peak_type in peak_types:
      # dictionary
      szDict = '%s_%s' % (selected_type, peak_type)
      rna_layout = rna_ellipse.rna_ellipse_layout[szDict]
      color = 'purple'
      for i in range(len(rna_layout)):
        color = rna_layout[0]
        if i == 0: continue
        
        szSplited = rna_layout[i].split(",")
        szStart = szSplited[0]
        szEnd = szSplited[1]
        
        szStartSplited = szStart.split()
        szEndSplited = szEnd.split()
        
        dIndirect1 = float(szStartSplited[0])
        dDirect1 = float(szStartSplited[1])
        dIndirect2 = float(szEndSplited[0])
        dDirect2 = float(szEndSplited[1])  
        
        # draw ornament? 
        if iFliped == 0:
          line = sparky.Line(self.spec.spectrum(), (dIndirect1, dDirect1), (dIndirect2, dDirect2))
        else:
          line = sparky.Line(self.spec.get(), (dDirect1, dIndirect1), (dDirect2, dIndirect2))
        line.color = color
        line.selected = 0
        
# ----------------------------------------------------------------------------
def show_ellipse_dialog(session):
  sputil.the_dialog(rna_ellipse_dialog,session).show_window(1)

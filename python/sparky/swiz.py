# -----------------------------------------------------------------------------
# Step-by-step Wizard
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: December 14, 2016
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#

import sparky
import sputil
import tkutil
import tkMessageBox

# First, Prev, Next, Button 1, Button 2, Button 3, Close
# Current Status

# -----------------------------------------------------------------------------
#
class swiz_dlg(tkutil.Dialog, tkutil.Stoppable):
  def __init__(self, session):
    tkutil.Dialog.__init__(self, session.tk, 'Step-by-step Tutorial Wizard')
    # Create label object
    self.lbTitle = tkutil.entry_row(self.top, 'First')
    self.lbTitle.frame.pack(side = 'top', anchor = 'w')

    # scrolling_list
    self.listbox = tkutil.scrolling_list(self.top, 'PLEASE READ BELOW ', 13)    
    self.listbox.frame.pack(side = 'top', fill = 'both', expand = 1)    
    
    # button    
    self.br = tkutil.button_row(self.top,
			   ('First', self.first_cb),
			   ('Previous', self.prev_cb),
			   ('Next', self.next_cb),
			   ('Button 1', self.btn1_cb),
			   ('Button 2', self.btn2_cb),
			   ('Button 3', self.btn3_cb),
			   ('Close', self.close_cb),
			   )
    self.br.frame.pack(side = 'top', anchor = 'w')			       
    

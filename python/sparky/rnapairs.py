# -----------------------------------------------------------------------------
# RNA-PAIRS support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: September 4, 2019
# 
# Please cite the following paper:
#   RNA-PAIRS: RNA probabilistic assignment of imino resonance shifts.
#     Bahrami A, Clos LJ II, Markley JL, Butcher SE, Eghbalnia HR.
#     J Biomol NMR. 2012 Apr;52(4):289-302. doi: 10.1007/s10858-012-9603-z.
#
# -----------------------------------------------------------------------------
#

import string
import Tkinter

import os
import apes
import pyutil
import sparky
import sputil
import tkutil
import tkMessageBox
import tkFileDialog

rnapairs_field = ('file01', 'file02')
rnapairs_types = ('N15_2D_HSQC', 'HH_2D_NOESY')
rnapairs_url = 'pine.nmrfam.wisc.edu'
rnapairs_selector = '/cgi-bin/pineiminouploader.cgi'
rna_spec_names = ('N-HSQC', 'exchangeable NOESY')
rna_specs = ('nhsqc', 'enoesy')

# -----------------------------------------------------------------------------
#
class rnapairs_dialog(tkutil.Dialog, tkutil.Stoppable):

  def __init__(self, session):

    self.session = session
    self.grid_widgets = []
    
    tkutil.Dialog.__init__(self, session.tk, 'RNA-PAIRS-SPARKY')
        
    # GUI
    self.spec_menu = []
    self.spec_pl = []
    for spec_name in rna_spec_names:
      m = apes.apes_menu(session, self.top, spec_name + ': ', allow_no_choice = 1)
      m.frame.pack(side = 'top', anchor = 'nw')
      self.spec_menu.append(m)
      self.spec_pl.append([])

      sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
      sep.pack(fill="both", padx=5,pady=5, side = 'top')        
      
    br = tkutil.button_row(self.top,
         ('Export to RNA-PAIRS', self.export_cb),
#   ('Submit', self.submit_cb),
         ('Close', self.close_cb),
         )
   
    br.frame.pack(side = 'top', anchor = 'w')     
    
  #--------------------------------------------------------------------------
#  def submit_cb(self):
#  
#---------------------------------------------------------------------------
  def export_cb(self):
    # check if both spectra available
    if (self.spec_menu[0].spectrum() == None) or (self.spec_menu[1].spectrum() == None):
      tkMessageBox.showerror('Error', 'Any of the spectra cannot be none.');
      return    
      
    if (self.spec_menu[0].spectrum().dimension != 2):
      tkMessageBox.showerror('Error', 'N-HSQC must be 2D spectrum.');
      return    
    
    if (self.spec_menu[1].spectrum().dimension != 2):  
      tkMessageBox.showerror('Error', 'H,H-NOESY ust be 2D spectrum.');
      return    
    
    #
    options = {}
    options['title'] = 'Select a directory to save input files.'
    path = tkFileDialog.askdirectory(**options) 
    for i in range(len(rna_spec_names)):
      realspec = self.spec_menu[i].spectrum()
            
      f = open(path + os.sep + realspec.name + '.list', 'w')
      szHeader = 'Assignment   w1   w2\n\n'
      f.write(szHeader)
      
      for peak in realspec.peak_list():
        szWrite = '?-?   '
        for i in range(realspec.dimension):
          szWrite = szWrite + '%9.3f' % (peak.frequency[i])
        szWrite = szWrite + '\n'
        f.write(szWrite)
      f.close()    
    tkMessageBox.showinfo('Export','You will be redicted to RNA-PAIRS web page.\nPlease prepare proper secondary structure file.');
    import webbrowser
    webbrowser.open('http://pine.nmrfam.wisc.edu/RNA')  
    
    
#
def export_rnapairs(session):
  sputil.the_dialog(rnapairs_dialog,session).show_window(1)    

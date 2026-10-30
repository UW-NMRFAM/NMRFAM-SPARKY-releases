# -----------------------------------------------------------------------------
# CS-Rosetta support
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Sep 10, 2014
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#

import sparky
import tkutil
import talos
import myseq
import tkMessageBox

def export_csrosetta(session):

  # Get sequence index
  # Sorting is included
  group_list = []
  sequence_from_session = myseq.BuildSequence(session, 3)
          
  sequence = myseq.CheckSequence(sequence_from_session)
  
  if myseq.GapInSequence(sequence) == 1: # there is a gap
    tkMessageBox.showinfo('Gap', 'There is a gap between your assignment.\nYou need to specify a sequence file.')
    sequence = myseq.LoadSeq(session, sequence)
    if sequence == None:
      tkMessageBox.showerror('Sequence', 'Sequence information is not satisfactory.')
      return
  
  #content = talos.GenerateTalos(session, sequence)
  #if content == '':    
  #  tkMessageBox.showinfo('Error', 'Error generating CS-Rosetta input file.')
  path = tkutil.save_file(session.tk, "Save to CS-Rosetta input file (TALOS)", "save to CS-Rosetta input in TALOS format")
  if not path: return
  if talos.WriteTalos(session, path, sequence) == 0:
    tkMessageBox.showinfo('TALOS+', 'Error writing TALOS-N file.') 
  else:  
    #if tkMessageBox.askyesno('Export','Finished. Do you want to run CS-Rosetta web server?'):
    #  tkMessageBox.showinfo('TALOS+', 'open.')    
    import webbrowser
    webbrowser.open('https://csrosetta.bmrb.wisc.edu/csrosetta')

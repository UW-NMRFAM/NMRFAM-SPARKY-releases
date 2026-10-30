# -----------------------------------------------------------------------------
# Get amino acid or nucleic acid sequence for molecules
#
import string
import Tkinter

import swalign
import myseq
import atomnames
import pyutil
import sputil
import tkutil
import tkMessageBox
import os

# -----------------------------------------------------------------------------
#
# Updated by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Dec 30, 2019
#
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Query user for sequence.
#
class sequencealignment_dialog(tkutil.Dialog):

  def __init__(self, session):

    self.molecule = None
    self.session = session  ## updated

    tkutil.Dialog.__init__(self, session.tk, 'Sequence Alignment (written by Woonghee Lee)')
    self.seq1 = tkutil.entry_field(self.top, 'Sequence 1', width=70)
    self.seq1.frame.pack(fill="both", side = 'top', anchor = 'w', expand=0)
    self.seq2 = tkutil.entry_field(self.top, 'Sequence 2', width=70)
    self.seq2.frame.pack(fill="both", side = 'top', anchor = 'w', expand=0)

    br = tkutil.button_row(self.top,
                           ('Align', self.align_cb),
                           ('Copy', self.copy_cb),
                           ('Close', self.close_cb),
               )
    br.frame.pack(fill="both", side = 'top', anchor = 'w')
    self.sa = tkutil.scrolling_list(self.top, 'Smith-Waterman Results', 11, \
                                    xscrollbar=True)
    self.sa.frame.pack(fill="both", side = 'top', anchor = 'w', expand=1)
  # ---------------------------------------------------------------------------
  #
  def align_cb(self):
    s1 = self.seq1.variable.get()
    s1 = s1.upper()
    s2 = self.seq2.variable.get()
    s2 = s2.upper()

    # clean s1 & s2
    Aline = 'ARNDCQEGHILKMFPSTWYVX'
    new_s1 = ''
    for a in s1:
      if a not in Aline: continue
      new_s1 += a
    new_s2 = ''
    for a in s2:
      if a not in Aline: continue
      new_s2 += a

    self.seq1.variable.set(new_s1)
    self.seq2.variable.set(new_s2)

    if len(new_s1) == 0 or len(new_s2) == 0: return
    align_results = swalign.do_swalign(new_s1, 1, new_s2, 1)

    # make sequence numbers
    seqnumline1, seqnumline2 = swalign.make_matchnumline(align_results)

    self.sa.clear()
    self.sa.append('* Smith-Watermann Alignment', [])
    self.sa.append('---------------------------', [])
    self.sa.append('SEQUENCE 1: ' + seqnumline1, [seqnumline1])
    self.sa.append('SEQUENCE 1: ' + align_results['matchsequence1'], \
                  [align_results['matchsequence1']])
    self.sa.append('MATCHING..: ' + align_results['matchline'], \
                  [align_results['matchline']])
    self.sa.append('SEQUENCE 2: ' + align_results['matchsequence2'], \
                  [align_results['matchsequence2']])
    self.sa.append('SEQUENCE 2: ' + seqnumline2, [seqnumline2])
    self.sa.append('---------------------------', [])
    self.sa.append('* SUM BLOSUM62: %d' % (align_results['sum_blosum62']), [])
    self.sa.append('* HOMOLOGY: %.3f %%' % (align_results['homology']), [])
    self.sa.append('* IDENTITY: %.3f %%' % (align_results['identity']), [])

  # ---------------------------------------------------------------------------
  #
  def copy_cb(self):
    line = ''
    for data in self.sa.line_data:
      line += (data[0]+'\n')
    #self.session.tk.clipboard_clear()
    #self.session.tk.clipboard_append(line)
    tkutil.write_to_clipboard(self.session, line)
    tkMessageBox.showinfo('Alignment results', \
                    'Alignment results are in your clipboard now.')
# ---------------------------------------------------------------------------
def show_sequencealignment_dialog(session):
  sputil.the_dialog(sequencealignment_dialog, session).show_window(1)

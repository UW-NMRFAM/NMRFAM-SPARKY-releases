
# -----------------------------------------------------------------------------
# PONDPRED-SPARKY
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Feb 3, 2020
# 
# Usage:
#
# 
# -----------------------------------------------------------------------------
#
import Tkinter
import myseq
import sparky
import tkutil
import sputil
import pyutil
import tkMessageBox
import os

Aline = 'ARNDCQEGHILKMFPSTWYV'

class pondpred_dialog(tkutil.Dialog):
  def __init__(self, session):
    self.molecule = None
    self.session = session
    tkutil.Dialog.__init__(self, session.tk, 'POND-PRED Dialog')


    # User name
    user_name_ef = tkutil.entry_field(self.top, 'Your name: ', initial = '', 
                                    width = 30)
    user_name_ef.frame.pack(side = 'top', anchor = 'w', expand = 0)
    self.user_name = user_name_ef.variable
    
    # User email
    user_email_ef = tkutil.entry_field(self.top, 'Your email: ', initial = '', 
                                      width = 30)
    user_email_ef.frame.pack(side = 'top', anchor = 'w')
    self.user_email = user_email_ef.variable    
    sep = Tkinter.Frame(self.top, height=2, bd=1, relief="ridge")
    sep.pack(fill="both", padx=5,pady=5, side = 'top', expand = 0)

    # Sequence entry
    se = self.sequence_entry(self.top)
    se.pack(side = 'top', anchor = 'w', fill = 'x', expand = 1)

    # check if file exists
    self.seq = None
    if session.project != None:
      if session.project.sparky_directory != '' and \
          os.path.exists(session.project.save_path):
        seq_path = session.project.save_path + '.seq'
        if os.path.exists(seq_path):
          self.file_field.variable.set(seq_path)
          self.seq = self.read_sequence()

    br = tkutil.button_row(self.top,
                ('Submit', self.submit_cb),
                ('Close', self.close_cb),
               )
    br.frame.pack(side = 'top', anchor = 'w')
  # ---------------------------------------------------------------------------
  #
  def submit_cb(self):
    s, f = self.read_sequence()
    if len(s) < 5:
      tkMessageBox.showerror('Error', \
        'Sequence is too short.')
      return
    if len(s) + f > 998:
      tkMessageBox.showerror('Error', \
        'Sequence is too long. Keep it under 999.')

    # get user name and email
    user_name = self.user_name.get()
    user_email = self.user_email.get()
    if user_name == '':      user_name = 'Anonymous'
    if user_email.find('@') == -1:
      tkMessageBox.showerror('Email', \
        'Your email is required to receive the POND-PRED results.')
      return
    
    # submit!
    fields = [['username', user_name],
              ['email', user_email],
              ['piname', 'PONDPRED-SPARKY'],
              ['institution', 'PONDPRED-SPARKY'],
              ['firstidx', str(f)],
              ['fasta', s],]
    
    import posthtml
    import httplib

    ponderosa_url = 'ponderosa.nmrfam.wisc.edu'
    ponderosa_selector = '/cgi-bin/ponderosa_predict.cgi'
    text=posthtml.post_multipart(ponderosa_url, ponderosa_selector, fields, [])
    tkMessageBox.showinfo('PONDEROSA job sumitted.', \
      'PONDEROSA job submitted. Check your result in your email inbox' + \
      ' after a few minutes. Please cite our Integrative NMR paper' + \
      'to support the maintenance (check with "n0").')
    
  # ---------------------------------------------------------------------------
  #
  def sequence_entry(self, parent):

    f = Tkinter.Frame(parent)

    h = Tkinter.Label(f, text = 'Sequence')
    h.pack(side = 'top', anchor = 'w')
    self.header = h
    
    t = tkutil.scrolling_text(f)
    t.text['wrap'] = 'char'
    t.frame.pack(side = 'top', fill = 'x', expand = 1)
    self.sequence_text = t

    ff = tkutil.file_field2(self.top, 'Sequence file', 'sequence', 
            file_type=[('3-letter-code sequence file with indices', '.seq'), 
                        ('1-letter-code sequence file', '.fasta'), 
                        ('3-letter-code sequence file without indices', '.txt')], 
            default_ext='.seq')
    ff.frame.pack(side = 'top', anchor = 'w')
    self.file_field = ff

    fr = tkutil.entry_field(f, 'First residue number', '1')
    fr.frame.pack(side = 'top', anchor = 'w')
    self.first_residue = fr

    return f

  # ---------------------------------------------------------------------------
  #
  def read_sequence(self):
    seq = ''
    path = self.file_field.get()
    if path:
      import myseq
      readseq = myseq.ReadSequenceFromFile(path)
      if len(readseq) == 0:
        result = tkMessageBox.askokcancel('Error', 'Wrong sequence file.')
        return
      else:
        for (iSeqIdx, szA) in readseq:
          seq = seq + szA
        self.first_residue.variable.set('%d' % (readseq[0][0]))
      self.sequence_text.text.delete('0.0', 'end')
      self.sequence_text.text.insert('0.0', seq)
    aa_sequence = self.sequence_text.text.get('0.0', 'end')
    aup = aa_sequence.upper()
    seq = ''.join(x for x in aup if myseq.Aline.find(x) != -1)
    # clean aa_sequence
    first_residue_number = pyutil.string_to_int(self.first_residue.variable.get(), 1)
    return seq, first_residue_number

def run_pondpred(session):
  sputil.the_dialog(pondpred_dialog, session).show_window(1)
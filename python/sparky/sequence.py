# -----------------------------------------------------------------------------
# Get amino acid or nucleic acid sequence for molecules
#
import string
import Tkinter

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
# Last updated: Oct 7, 2019
# 
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Query user for sequence.
#
class sequence_dialog(tkutil.Dialog):

  def __init__(self, session):

    self.molecule = None
    self.session = session  ## updated
    
    tkutil.Dialog.__init__(self, session.tk, 'Sequence Entry')

    se = self.sequence_entry(self.top)
    se.pack(side = 'top', anchor = 'w', fill = 'x', expand = 1)

    br = tkutil.button_row(self.top,
              ('Ok', self.ok_cb),
              ('Cancel', self.close_cb),
              ('Help', sputil.help_cb(session, 'Sequence')),
               )
    br.frame.pack(side = 'top', anchor = 'w')
      
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
    first_residue_number = \
        pyutil.string_to_int(self.first_residue.variable.get(), 1)
    s = sequence(aa_sequence, first_residue_number)
    return s

  # ---------------------------------------------------------------------------
  #
  def ok_cb(self):
    session = self.session
    seq = self.read_sequence()
    if self.molecule:
      set_molecule_sequence(self.molecule, seq)
    ###########################################################################
    # This is updated part for integration.      
    # If project file name exists, the name + '.seq' will be saved.
    # by Woonghee Lee
    ###########################################################################    
    # check if sequence file exists
    try:
      seq_path = session.project.save_path + '.seq'
    except:
      seq_path = ''

    try:
      result = True
      if os.path.exists(seq_path):
        result = tkMessageBox.askokcancel('Stored sequence file found.', \
                  'Do you want to overwrite to stored sequence file?')
      
      if result is True:  
        import myseq
        # build sequence
        seq_list = []
        iIdx = seq.first_residue_number
        for szA in seq.one_letter_codes:
          seq_list.append((iIdx, szA))
          iIdx = iIdx + 1
        myseq.WriteSequenceToFile(seq_path, seq_list)
    except:
      pass    
      
    self.close_cb()

  # ---------------------------------------------------------------------------
  #
  def set_molecule(self, molecule):

    self.molecule = molecule
    
    if molecule and molecule.name:
      self.header['text'] = 'Sequence for %s molecule' % molecule.name
    else:
      self.header['text'] = 'Sequence'

    self.sequence_text.text.delete('0.0', 'end')

    if molecule:
      seq = has_molecule_sequence(molecule)
      if seq:
        self.sequence_text.text.insert('0.0', seq.one_letter_codes)

  # ---------------------------------------------------------------------------
  #
  def get_sequence(self, molecule):

    self.set_molecule(molecule)
    self.return_when_closed()

# -----------------------------------------------------------------------------
#
def has_molecule_sequence(molecule):

  if not hasattr(molecule, 'sequence'):
    s = molecule.saved_value('sequence')
    f = molecule.saved_value('first_residue_number')
    if s == None or f == None:
      molecule.sequence = None
    else:
      f = pyutil.string_to_int(f)
      molecule.sequence = sequence(s, f)
  return molecule.sequence

# -----------------------------------------------------------------------------
#
def set_molecule_sequence(molecule, seq):

  if seq:
    s = seq.one_letter_codes
    f = seq.first_residue_number
    molecule.save_value('sequence', s)
    molecule.save_value('first_residue_number', repr(f))
  molecule.sequence = seq

# -----------------------------------------------------------------------------
# Return the molecule sequence.  Query user if it is not known.
#
def molecule_sequence(molecule):

  seq = has_molecule_sequence(molecule)
  if seq == None:
    d = sputil.the_dialog(sequence_dialog, molecule.session)
    d.get_sequence(molecule)

  return has_molecule_sequence(molecule)
      
# -----------------------------------------------------------------------------
#
class sequence:

  def __init__(self, one_letter_codes, first_residue_number):

    olc = olc2 = ''
    for symbol in one_letter_codes:
      if not symbol in string.whitespace:
        olc = olc + string.capitalize(symbol)
        olc2 = olc2 + symbol
    self.bt = myseq.GetBiomoleculeTypeByFasta(olc)
    if self.bt == 'p':
      self.one_letter_codes = olc
    else:
      self.one_letter_codes = olc2 # keep cases for nucleic acids

    n2s = self.number_to_symbol_table(olc, first_residue_number)
    self.number_to_symbol = n2s
                                                        
    self.first_residue_number = first_residue_number
    self.last_residue_number = first_residue_number + len(n2s) - 1

    self.resonances = self.create_resonances()

    nsa_to_res = {}
    for r in self.resonances:
      nsa_to_res[(r.number, r.symbol, r.atom_name)] = r
    self.nsa_to_resonance = nsa_to_res

    ga_to_res = {}
    for r in self.resonances:
      ga_to_res[r.group_atom] = r
    self.group_atom_to_resonance = ga_to_res
    
  # ---------------------------------------------------------------------------
  #
  def number_to_symbol_table(self, one_letter_codes, first_residue_number):

    ns_table = {}
    number = first_residue_number
    for symbol in one_letter_codes:
      ns_table[number] = symbol
      number = number + 1
    return ns_table

  # ---------------------------------------------------------------------------
  #
  def create_resonances(self):
    rlist = []
    for number, symbol in self.number_to_symbol.items():
      if self.bt == 'p':
        for atom_name in atomnames.protein_atoms_by_group[symbol]:
          r = resonance(number, symbol, atom_name)
          rlist.append(r)
      else:    
        for atom_name in atomnames.dna_rna_atoms_by_group[symbol.upper()]:
          r = resonance(number, symbol, atom_name)
          rlist.append(r)
    return rlist
    
  # ---------------------------------------------------------------------------
  #
  def resonance(self, number, symbol, atom_name):

    nsa = (number, symbol, atom_name)
    if self.nsa_to_resonance.has_key(nsa):
      return self.nsa_to_resonance[nsa]
    return None
    
  # ---------------------------------------------------------------------------
  #
  def peak_resonances(self, peak):

    res = []
    for r in peak.resonances():
      seq_r = self.resonance(r.group.number, r.group.symbol, r.atom.name)
      res.append(seq_r)
    return tuple(res)
  
# -----------------------------------------------------------------------------
#
class resonance:

  def __init__(self, number, symbol, atom_name):
    
    self.number = number
    self.symbol = symbol
    self.atom_name = atom_name
    self.group_name = symbol + repr(number)
    self.group_atom = (self.group_name, atom_name)

# -----------------------------------------------------------------------------
# Show molecule sequence dialog
#
def show_sequence_dialog(session):

  d = sputil.the_dialog(sequence_dialog, session)
  s = session.selected_spectrum()
  if s:
    if len(s.molecule.group_list()) != 0:
      d.set_molecule(s.molecule)
      d.show_window(1)
      return
  if session.project != None:
    seq_path = session.project.save_path + '.seq'
    if os.path.exists(seq_path):
      d.file_field.set(seq_path)
  d.show_window(1)
  d.read_sequence()

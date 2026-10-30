# -----------------------------------------------------------------------------
# PDB2CIF - Generate mmCIF using old PDB file
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Nov 13, 2017
# 
# Usage:
#   python ./pdb2cif [PDB file] [mmCIF file]
#
# Note. This script only converts very simply file from PONDEROSA
# 
# -----------------------------------------------------------------------------

import os, sys

usage_print = """
Usage:
  python ./pdb2cif [PDB file] [mmCIF file] 
"""

entity_poly_seq_header = """# 
loop_
_entity_poly_seq.entity_id 
_entity_poly_seq.num 
_entity_poly_seq.mon_id 
_entity_poly_seq.hetero 
"""

atom_header = """# 
loop_
_atom_type.symbol 
C 
H 
N 
O 
S 
# 
loop_
_atom_site.group_PDB 
_atom_site.id 
_atom_site.type_symbol 
_atom_site.label_atom_id 
_atom_site.label_alt_id 
_atom_site.label_comp_id 
_atom_site.label_asym_id 
_atom_site.label_entity_id 
_atom_site.label_seq_id 
_atom_site.pdbx_PDB_ins_code 
_atom_site.Cartn_x 
_atom_site.Cartn_y 
_atom_site.Cartn_z 
_atom_site.occupancy 
_atom_site.B_iso_or_equiv 
_atom_site.pdbx_formal_charge 
_atom_site.auth_seq_id 
_atom_site.auth_comp_id 
_atom_site.auth_asym_id 
_atom_site.auth_atom_id 
_atom_site.pdbx_PDB_model_num 
"""

def pdb2cif(pdb_file, cif_file, HETATM=False):
  pdb_name = (cif_file.split('/')[-1]).split('.')[0]
  pdb_header = 'data_'+pdb_name+'\n#\n_entry.id  '+pdb_name+'\n'

  if not os.path.exists(pdb_file):
    print "PDB file not found."  
    print usage_print
    return False

  # read PDB lines  
  f = open(pdb_file, 'r')
  pdb_lines = f.readlines()
  f.close()

  # read atoms & models...
  model_list = []
  for line in pdb_lines:
    if len(line) < 10: continue
    if line[0:5] == 'MODEL':
      model_list.append([])
      atom_list = model_list[-1]
    if line[0:4] != 'ATOM' and line[0:6] != 'HETATM': continue
    if not HETATM and line[0:6] == 'HETATM': continue
    atom_list.append(line)

  # sequence information
  pdbx_line = pdb_header+entity_poly_seq_header
  atom_list = model_list[0]
  for atom in atom_list:
    atom_type = atom[12:16].strip()
    if atom_type != 'CA': continue
    seq_type = atom[17:20].strip()
    seq_num = int(atom[23:26].strip())
    line = '1 %-4d %s n\n' % (seq_num, seq_type)
    pdbx_line = pdbx_line + line
  pdbx_line = pdbx_line + '#\n'

  # atom information
  pdbx_line = pdbx_line + atom_header
  for i in range(len(model_list)):
    atom_list = model_list[i]
    for line in atom_list:
      serial = line[6:11].strip()
      atom_name = line[12:16].strip()
      res_name = line[17:20].strip()
      chain_name = line[21:22]
      seq_num = int(line[22:26].strip())
      x_coord = line[30:38].strip()
      y_coord = line[39:46].strip()
      z_coord = line[47:54].strip()
      temp_fact = line[60:66].strip()
      if line [0:4] == 'ATOM':
        xline = 'ATOM %-5s %1s %-4s . %3s %1s 1 %-2d ? %8s %8s %8s 1.00 %-5s ? %-2d %3s %1s %-4s %-3d\n' % (serial, atom_name[0], atom_name, res_name, chain_name, seq_num, x_coord, y_coord, z_coord, temp_fact, seq_num, res_name, chain_name, atom_name, i+1)
      else:
        xline = 'HETATM %-3s %1s %-4s . %3s %1s 1 %-2d ? %8s %8s %8s 1.00 %-5s ? %-2d %3s %1s %-4s %-3d\n' % (serial, atom_name[0], atom_name, res_name, chain_name, seq_num, x_coord, y_coord, z_coord, temp_fact, seq_num, res_name, chain_name, atom_name, i+1)
      pdbx_line = pdbx_line + xline
  pdbx_line = pdbx_line + '#\n'
      
  f = open(cif_file, 'w')
  f.write(pdbx_line) 
  f.close()
  return True

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "Not enough argument found."  
    print usage_print
    sys.exit()
  
  pdb_file = sys.argv[1]
  cif_file = sys.argv[2]
  pdb2cif(pdb_file, cif_file)

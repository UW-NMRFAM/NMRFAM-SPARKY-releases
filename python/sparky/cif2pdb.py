# -----------------------------------------------------------------------------
# CIF2PDB - Generate old PDB using mmCIF file
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: Sep 12, 2019
# 
# Usage:
#   python ./cif2pdb [mmCIF file] [PDB file]
#
# Note. This script only converts very simple mmCIF file
# 
# -----------------------------------------------------------------------------

import os, sys

usage_print = """
Usage:
  python ./cif2pdb [mmCIF file] [PDB file] 
"""
def cif2pdb(cif_file, pdb_file, HETATM=False):
  if not os.path.exists(cif_file):
    print "mmCIF file not found."  
    print usage_print
    return False

  # read PDB lines  
  f = open(cif_file, 'r')
  cif_lines = f.readlines()
  f.close()

  # read atoms & models...
  model_list = list(map(lambda x: [], range(1000)))
  iStart = -1
  iEnd = len(cif_lines)

  field_list = []
  for i in range(len(cif_lines)):
    if iStart != -1: break
    line = cif_lines[i]
    if line.find('_atom_site.group_PDB') != -1:
      for j in range(i, len(cif_lines)):
        # get start and end point
        line2 = cif_lines[j]
        if line2[0:4] == 'ATOM': 
          iStart = j
          for k in range(j, len(cif_lines)):
            if cif_lines[k].strip() == '#':
              iEnd = k
              break
          break
      # get field names    
      for j in range(i, iStart):
        line2 = cif_lines[j]
        if line2.find('_atom_site.') != -1:
          field_list.append(line2.strip())
  if iStart == -1:
    print "mmCIF file is incorrect or corrupted."  
    return False
  
  id_idx = field_list.index('_atom_site.id')
  nuclei_idx = field_list.index('_atom_site.type_symbol')
  atom_idx = field_list.index('_atom_site.label_atom_id')
  aaa_idx = field_list.index('_atom_site.label_comp_id')
  seqid_idx = field_list.index('_atom_site.label_seq_id')
  x_idx = field_list.index('_atom_site.Cartn_x')
  y_idx = field_list.index('_atom_site.Cartn_y')
  z_idx = field_list.index('_atom_site.Cartn_z')
  occ_idx = field_list.index('_atom_site.occupancy')

  try:
    chain_idx = field_list.index('_atom_site.label_asym_id')
  except:
    chain_idx = -1
  try:
    B_idx = field_list.index('_atom_site.B_iso_or_equiv')
  except:
    B_idx = -1
  try:
    model_idx = field_list.index('_atom_site.pdbx_PDB_model_num')
  except:
    model_idx = -1

  # parse ATOM fields
  for i in range(iStart, iEnd):
    line = cif_lines[i].strip()
    if len(line) < 20: continue
    if line[0:4] != 'ATOM' or line[0:6] != 'HETATM': continue
    if not HETATM and line[0:6] == 'HETATM': continue
    sp = line.split()
    
    # MODEL ID
    model_id = 1
    try:
      model_id = int(sp[model_idx])
    except:
      pass
    # B Factor
    Bfac = 0.0
    try:
      Bfac = float(sp[B_idx])
    except:
      pass
    # CHAIN_ID
    chain_id = ' '
    try:
      chain_id = sp[chain_idx]
    except:
      pass
    
    try:
      id = int(sp[id_idx])
      nuclei_id = sp[nuclei_idx]
      atom_id = sp[atom_idx]
      aaa_id = sp[aaa_idx]
      seqid = int(sp[seqid_idx])
      x = float(sp[x_idx])
      y = float(sp[y_idx])
      z = float(sp[z_idx])
      occ = float(sp[occ_idx])
    except:
      continue
    if line[0:4] == 'ATOM':
      pdb_line = 'ATOM   %4d %4s%4s %1s %3d     %7.3f %7.3f %7.3f %5.2f %5.2f           %s\n' \
          % (id, atom_id, aaa_id, chain_id, seqid, x, y, z, occ, Bfac, nuclei_id)
    else:
      pdb_line = 'HETATM %4d %4s%4s %1s %3d     %7.3f %7.3f %7.3f %5.2f %5.2f           %s\n' \
          % (id, atom_id, aaa_id, chain_id, seqid, x, y, z, occ, Bfac, nuclei_id)
    model_list[model_id].append(pdb_line)
    
  # write per model
  pdb_lines = ''
  for i in range(1000):
    mdl = model_list[i]
    if len(mdl) == 0: continue
    line = 'MODEL      %3d\n' % (i)
    pdb_lines = pdb_lines + line
    for pdb_line in mdl:
      pdb_lines = pdb_lines + pdb_line
    # TERMINATOR
    endmdl = 'TER    ' + pdb_line[7:11] + '      ' + pdb_line[17:26] + '\n'
    pdb_lines = pdb_lines + endmdl + 'ENDMDL\n'
  f = open(pdb_file, 'w')
  f.write(pdb_lines)
  f.close()
  return True

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "Not enough argument found."  
    print usage_print
    sys.exit()
  
  cif_file = sys.argv[1]
  pdb_file = sys.argv[2]
  cif2pdb(cif_file, pdb_file)

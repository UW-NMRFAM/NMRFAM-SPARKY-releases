# ---------------------------------------------------------------------------
# Amino acid chemical shift statistics from ncIDP-Library
#
# by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: September 20, 2014
# 
# -----------------------------------------------------------------------------
#
# Originated from:
#
# ncIDP-Library Based Repositioning Plugin for Sparky NMR Assignment Software
# Authors:
#      Kamil Tamiola (k.tamiola@rug.nl)
#      Frans A.A. Mulder (f.a.a.mulder@rug.nl)
#

import string
import sys
import os

import sputil
import atomnames
import sequence
import sparky
import pyutil

ncIDP_cs =  (
"A   0.088   8.158   -0.056   -0.046   4.224   -0.042    0.068   178.418   -0.816   0.161   52.599   -0.187   -0.135   19.102   0.018  -0.639   123.906   -0.004",
"R   0.251   8.232   -0.039   -0.004   4.239   -0.017   -0.246   176.821   -0.625   0.029   56.088   -0.258   -0.038   30.691   0.046   1.909   121.288   -0.065",
"D   0.081   8.217   -0.003   -0.024   4.537   -0.009    0.059   176.987   -0.853   0.290   54.331   -0.095   -0.182   41.089   0.079   0.679   120.207   -0.373",
"N   0.130   8.366   -0.023   -0.004   4.632   -0.033   -0.052   175.825   -0.849   0.293   53.231   -0.067   -0.205   38.790  -0.013   0.699   118.668   -0.219",
"C   0.293   8.410    0.375    0.025   4.447   -0.008   -0.417   174.927   -0.610  -0.006   58.327    0.047    0.008   28.085  -0.170   3.100   119.068    0.785",
"E   0.174   8.304   -0.014   -0.048   4.222   -0.005   -0.032   177.125   -0.503   0.171   56.650   -0.071   -0.119   30.225   0.065   1.226   120.769   -0.100",
"Q   0.225   8.258   -0.016   -0.009   4.254   -0.039   -0.153   176.510   -0.551   0.125   55.840   -0.098   -0.064   29.509   0.004   1.700   120.224   -0.087",
"G   0.000   8.307    0.000    0.000   3.980    0.000    0.000   174.630    0.000   0.000   45.236    0.000    0.000    0.000   0.000   0.000   108.783    0.000",
"H   0.141   8.310   -0.136   -0.019   4.585   -0.059   -0.243   175.349   -0.677   0.069   55.964   -0.248   -0.093   29.719   0.041   1.761   118.930   -0.225",
"I   0.250   7.963   -0.071    0.010   4.076    0.000   -0.045   176.897   -0.559  -0.087   61.247   -0.129   -0.111   38.563   0.093   4.205   120.512   -0.167",
"L   0.105   8.088   -0.086   -0.042   4.260   -0.021   -0.115   178.037   -0.612   0.083   55.260   -0.184   -0.143   42.212  -0.053   0.835   121.877   -0.397",
"K   0.174   8.221   -0.053   -0.031   4.237   -0.011   -0.117   177.224   -0.520   0.195   56.412   -0.142   -0.102   32.921   0.029   1.311   121.353    0.068",
"M   0.205   8.209   -0.066   -0.018   4.425   -0.018   -0.118   176.953   -0.271   0.028   55.591   -0.061   -0.139   32.690  -0.205   1.407   120.002   -0.145",
"F   0.079   8.107   -0.133   -0.040   4.573   -0.052   -0.672   176.368   -0.891  -0.163   57.934   -0.247    0.059   39.660   0.023   2.238   120.138   -0.484",
"P   0.292   0.000   -0.028   -0.032   4.337    0.276   -0.040   177.542   -2.874   0.021   63.180   -2.423   -0.151   32.072  -0.426   0.569   136.612    1.072",
"S   0.230   8.215   -0.002    0.006   4.392    0.030   -0.128   175.236   -0.483   0.155   58.352   -0.151   -0.153   63.766   0.087   2.297   115.935   -0.053",
"T   0.211   8.047    0.042   -0.005   4.252    0.065   -0.130   175.122   -0.327   0.143   61.926   -0.122   -0.072   69.794   0.086   2.680   114.024    0.076",
"W  -0.555   7.725    0.032   -0.168   4.567   -0.082   -0.465   174.549   -0.694   0.014   57.500   -0.201   -0.046   29.380   0.069   0.795   120.733   -0.273",
"Y  -0.052   8.026   -0.093   -0.035   4.504   -0.044   -0.633   176.284   -0.848  -0.245   57.761   -0.148    0.017   38.750   0.019   2.729   120.228   -0.387",
"V   0.259   8.037   -0.052   -0.007   4.009    0.021   -0.198   176.772   -0.662   0.075   62.347   -0.214   -0.147   32.674   0.044   4.507   120.403   -0.047",
)
ncIDP_dev = (
"A    0.003    0.003    0.002   0.001    0.001    0.001   0.006    0.007    0.007   0.004    0.005    0.004   0.004    0.005    0.004   0.015    0.016    0.014",
"R    0.003    0.003    0.003   0.001    0.001    0.001   0.008    0.008    0.007   0.005    0.005    0.005   0.005    0.005    0.005   0.021    0.019    0.018",
"D    0.003    0.003    0.003   0.001    0.001    0.001   0.007    0.009    0.007   0.005    0.007    0.005   0.006    0.006    0.005   0.016    0.020    0.018",
"N    0.003    0.004    0.003   0.051    0.004    0.001   0.008    0.009    0.007   0.005    0.006    0.005   0.006    0.006    0.005   0.018    0.022    0.020",
"C    0.002    0.003    0.003   0.003    0.008    0.001   0.007    0.007    0.007   0.007    0.007    0.007   0.006    0.004    0.005   0.002    0.022    0.020",
"E    0.003    0.003    0.003   0.001    0.001    0.001   0.006    0.007    0.005   0.004    0.005    0.004   0.005    0.005    0.004   0.014    0.016    0.015",
"Q    0.003    0.003    0.003   0.001    0.001    0.001   0.008    0.008    0.007   0.005    0.006    0.005   0.005    0.006    0.005   0.019    0.019    0.018",
"G    0.000    0.003    0.000   0.001    0.004    0.001   0.000    0.007    0.000   0.000    0.005    0.000   0.000    0.000    0.000   0.000    0.017    0.000",
"H    0.004    0.005    0.004   0.001    0.054    0.001   0.010    0.011    0.009   0.006    0.007    0.007   0.007    0.010    0.006   0.023    0.030    0.026",
"I    0.003    0.004    0.004   0.001    0.001    0.001   0.012    0.010    0.012   0.008    0.009    0.007   0.008    0.006    0.009   0.024    0.024    0.023",
"L    0.003    0.003    0.003   0.001    0.001    0.001   0.007    0.008    0.007   0.005    0.006    0.005   0.005    0.005    0.005   0.017    0.020    0.018",
"K    0.003    0.003    0.003   0.001    0.001    0.001   0.006    0.007    0.007   0.004    0.005    0.004   0.004    0.005    0.004   0.015    0.018    0.015",
"M    0.005    0.005    0.005   0.048    0.139    0.044   0.009    0.015    0.014   0.009    0.010    0.010   0.009    0.010    0.011   0.032    0.031    0.031",
"F    0.004    0.004    0.005   0.048    0.001    0.044   0.015    0.011    0.008   0.006    0.007    0.007   0.007    0.009    0.008   0.025    0.029    0.026",
"P    0.003    0.000    0.003   0.001    0.001    0.001   0.007    0.009    0.011   0.005    0.006    0.006   0.005    0.005    0.008   0.017    0.044    0.019",
"S    0.003    0.003    0.003   0.001    0.001    0.001   0.007    0.007    0.006   0.004    0.005    0.004   0.004    0.005    0.004   0.013    0.017    0.016",
"T    0.003    0.003    0.003   0.001    0.001    0.001   0.007    0.007    0.006   0.005    0.006    0.005   0.004    0.005    0.004   0.016    0.019    0.017",
"W    0.003    0.003    0.003   0.023    0.002    0.002   0.007    0.007    0.007   0.014    0.008    0.005   0.003    0.005    0.004   0.085    0.031    0.023",
"Y    0.005    0.005    0.004   0.165    0.217    0.127   0.012    0.009    0.009   0.008    0.008    0.008   0.008    0.008    0.007   0.030    0.028    0.026",
"V    0.003    0.003    0.003   0.085    0.001    0.001   0.007    0.007    0.007   0.005    0.005    0.004   0.005    0.005    0.005   0.019    0.021    0.017",
)

class atom_stats:
  """
    ****************************
  v 1.0 | 11th March 2010 | kT
  ****************************
  Atom Statistics Class adopted from Sparky:
    gsym            -> amino acid one letter code
    atom_name       -> type of nucleus
    group_numerb    -> sequence number
    average_shift   -> sequence specific random coil shift
    shift_deviation -> sequence specific chemical shift deviation
  """
  def __init__(self, gsym, aname, gnumber, fave, fdev):

    self.group_symbol = gsym
    self.atom_name = aname
    self.group_number = gnumber
    self.average_shift = fave
    self.shift_deviation = fdev


# -----------------------------------------------------------------------------
def atom_statistics(group_number, group_symbol, atom_name, ast):
  key = (group_number, group_symbol, atom_name)
  if ast.has_key(key):
    return ast[key]
  
  return None

def resonance_statistics(reslist):
  """
  Updated by Woonghee Lee from NMRFAM
  Oct. 23, 2014

    Compute global, sequence-specific ncIDP-based chemical shifts using resonance list
  """
  r = reslist[0]
  seq = sequence.molecule_sequence(r.condition.molecule).one_letter_codes
  prediction = compute_RC(ncIDP_cs, ncIDP_dev, seq)
  return prediction

def single_resonance_statistics(r):
  """
  Updated by Woonghee Lee from NMRFAM
  Oct. 23, 2014

    Compute global, sequence-specific ncIDP-based chemical shifts using resonance list
  """
  seq = sequence.molecule_sequence(r.condition.molecule).one_letter_codes
  prediction = compute_RC(ncIDP_cs, ncIDP_dev, seq)
  return prediction

def sequence_resonance_statistics(tmp):
  """
  Updated by Woonghee Lee from NMRFAM
  Oct. 23, 2014
  
    Compute global, sequence-specific ncIDP-based chemical shifts using FASTA sequence
  """
  seq = tmp.one_letter_codes
  prediction = compute_RC(ncIDP_cs, ncIDP_dev, seq)
  return prediction

def read_File(ncIDP_matrix):
  """
  Updated by Woonghee Lee from NMRFAM
  Oct. 23, 2014

  ****************************
  v 1.0 | 11th March 2010 | kT
  ****************************
  Read an ACSII file and return a list o lines without the new-line character
  """
  #star_data=open(filename).readlines()            # Start reading file-by-file
  separated=[]

  for p in range (len(ncIDP_matrix)):                # Separate elements
    separated.append(ncIDP_matrix[p].split())  
  return separated

def read_ncIDP_table(fi):
  """
  Updated by Woonghee Lee from NMRFAM
  Oct. 23, 2014

  ****************************
  v 1.0 | 11th March 2010 | kT
  ***************************
  Read ncIDP chemical shift table and return structured dictionary
  Important:
  - anything after REMARK keyword is ignored
      - first column contains amino acid type
      - there are 18 columns organized in triplets
        - within every triplet column 1 is the correction for the left-neighbour
      - 2nd is the value for the central residue
      - 3rd is the correction for the right-neighbour
      - triplet order corresponds to:
          H HA C CA CB N
        nuclei order! Keep it that way! Otherwise modify cs(list) within read_ncIDP_table function!
  """
  cs = ['H','HA','C','CA','CB','N']
  table = {}
  data = read_File(fi)
  for l in data:
    if not l[0]=='REMARK':
      table[l[0]]={}
      for s in range(len(cs)):
        table[l[0]][cs[s]]={}
        table[l[0]][cs[s]]['p']=float(l[1+s*3])
        table[l[0]][cs[s]]['c']=float(l[2+s*3])
        table[l[0]][cs[s]]['n']=float(l[3+s*3])
  return table

atom_stat_table = None
def compute_RC(idp_cs, idp_dev, seq):
  """
    ****************************
    v 1.0 | 11th March 2010 | kT
    ****************************
    Compute neighbor-corrected random coil chemical shifts and their deviations for an arbitrary 
    protein sequence using ncIDP library
  """
  cs = ['H','HA','C','CA','CB','N']
  RC={}
  ncIDP_shifts = read_ncIDP_table(idp_cs)
  ncIDP_devs = read_ncIDP_table(idp_dev)
  for res in range(1,len(seq)+1):
    i = res - 1 # This is the actual python index
    RC[res]={}
    RC[res]['symbol']=seq[i]
    for n in cs: 
      RC[res][n]={}
      if i!=0 and i<len(seq)-1:
        RC[res][n]['cs']=ncIDP_shifts[seq[i-1]][n]['p']+ncIDP_shifts[seq[i]][n]['c']+ncIDP_shifts[seq[i+1]][n]['n']
        RC[res][n]['dev']=ncIDP_devs[seq[i-1]][n]['p']+ncIDP_devs[seq[i]][n]['c']+ncIDP_devs[seq[i+1]][n]['n']
      else:
        if i==0:
          RC[res][n]['cs']=ncIDP_shifts[seq[i]][n]['c']+ncIDP_shifts[seq[i+1]][n]['n']
          RC[res][n]['dev']=ncIDP_devs[seq[i]][n]['c']+ncIDP_devs[seq[i+1]][n]['n']
        else:
          RC[res][n]['cs']=ncIDP_shifts[seq[i-1]][n]['p']+ncIDP_shifts[seq[i]][n]['c']
          RC[res][n]['dev']=ncIDP_devs[seq[i-1]][n]['p']+ncIDP_devs[seq[i]][n]['c']        
  # Now change the structure of the dictionary so we can directly inject it into Sparky
  global atom_stat_table
  if atom_stat_table == None:
    atom_stat_table = {}
  for resid in RC.keys():
    for n in cs:
      if (seq[resid-1]=='G' and n=='CB') or (seq[resid-1]=='P' and n=='H'): continue
      gsym = RC[resid]['symbol']
      gnumber = resid
      aname = n
      fave = RC[resid][n]['cs']
      fdev = RC[resid][n]['dev']
      atom_stat_table[(resid, RC[resid]['symbol'], n)]=atom_stats(gsym, aname, gnumber, fave, fdev)
  return atom_stat_table

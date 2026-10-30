# -----------------------------------------------------------------------------
# CHESCA INI SUPPORT
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: August 2, 2019
# 
#
# -----------------------------------------------------------------------------
# CITATION: TBA
#
# -----------------------------------------------------------------------------


#####################################################################
# INI I/O IMPLEMENTATION
#####################################################################
def ReadFileLines(path):
  f = open(path, 'r')
  lines = f.readlines()
  f.close()
  return lines

def SaveFileLines(path, lines):
  f = open(path, 'w')
  for line in lines:
    f.write(line.strip() + '\n')
  f.close()
  
def FindIniSection(lines, section):
  iStart = 10**9
  iEnd = -10**9
  key_start = '[' + section + ']'
  key_end =  '[' + section + '_END]'
  for i in range(len(lines)):
    line = lines[i].strip()
    if line == key_start: iStart = i
    if line == key_end: iEnd = i
    if iEnd > iStart: break
  return iStart, iEnd

def FindIniKey(lines, section_start, section_end, key):
  for i in range(section_start, section_end+1):
    line = lines[i]
    if line.find(key + '=') != -1:
      return i
  return -1

def GetIniString(lines, section, key):  
  iStart, iEnd = FindIniSection(lines, section)
  if iEnd < iStart: return ''
  iKeyIdx = FindIniKey(lines, iStart, iEnd, key)
  if iKeyIdx == -1: return ''
  return lines[iKeyIdx].replace(key+'=', '').strip()

def LoadIniString(ini_path, section, key):
  lines = ReadFileLines(ini_path)
  return GetIniString(lines, section, key)
#####################################################################

def GetStatesFromChescaIni(lines):
  state_list = []
  for i in range(1, 20):
    szSection = 'STATE%d' % (i)
    state_name = GetIniString(lines, szSection, 'NAME')
    if state_name == '': break
    state_list.append(state_name)
  return state_list

def GetRcutoffFromChescaIni(lines):
  return float(GetIniString(lines, 'OPTIONS', 'RCUTOFF'))

def GetR2cutoffFromChescaIni(lines): # cluster cutoff
  return float(GetIniString(lines, 'OPTIONS', 'R2CUTOFF'))  

def GetHzPerPpmFromChescaIni(lines, state_name=None, state_key=None):
  if state_name != None:
    state_list = GetStatesFromChescaIni(lines)
    idx = state_list.index(state_name)
    sk = 'STATE%d' % (idx+1)
  else:
    sk = state_key
  nhz2ppm = GetIniString(lines, sk, 'NHZPERPPM')
  hhz2ppm = GetIniString(lines, sk, 'HHZPERPPM')
  return nhz2ppm, hhz2ppm

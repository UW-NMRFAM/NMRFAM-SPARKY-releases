# -----------------------------------------------------------------------------
# Read and use ShiftX2 CSV format output
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: September 8, 2014
# 
# -----------------------------------------------------------------------------

import tkMessageBox

# -----------------------------------------------------------------------------    
# from assignment
""" csv output format
NUM,RES,ATOMNAME,SHIFT
1,G,C,171.2038
1,G,CA,43.7794
1,G,H,8.1130
1,G,HA,4.2181
1,G,HA2,4.1176
1,G,HA3,4.0431
1,G,N,110.3070
2,P,C,176.9662
"""
def FetchShiftX2(szURL):
  # if szURL starts with 'www', put 'http://'
  # else if 'http:', none
  # else, put 'file://'
  iType = 0   # 0: http, 1: www, 2: local
  if len(szURL) < 6: iType = 2
  elif szURL[0:3] == 'www': iType = 1
  elif szURL[0:4] != 'http': iType = 2
  if iType == 1: szURL = 'http://' + szURL
  if iType < 2:  # url
    try: 
      import urllib2
    except:
      tkMessageBox.showerror('urllib2', 'You do not have openssl installed or set properly.\nPlease download .csv file to your local machine.');
      return []
    try:  
      response = urllib2.urlopen(szURL)
    except:
      tkMessageBox.showerror('URL','URL for your shift file is not correct.');
      return []
    csv_lines = response.readlines()
  else:   # file type
    try:
      f = open(szURL, 'r')
    except:  
      tkMessageBox.showerror('PATH','File path for your shift csv is not correct.');
      return []
    csv_lines = f.readlines()
    f.close()
  
  shiftx2_pred_list = []

  for line in csv_lines:
    split_line = line.strip().split(',')
    if len(split_line) != 4: continue   # num, res, atomname, shift
    if split_line[0] == 'NUM': continue # header...
    try:
      shiftx2_pred_list.append( (int(split_line[0]), split_line[1], split_line[2], float(split_line[3]) ) )
    except:
      continue  
  return shiftx2_pred_list  


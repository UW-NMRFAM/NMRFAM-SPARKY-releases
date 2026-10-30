# -----------------------------------------------------------------------------
# Chemical shift-based cis/trans Proline prediction
# 
# -----------------------------------------------------------------------------
# by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last Update: Sep 10, 2019
# 
# Based on: 
#    - Shen & Bax, PROMEGA, JBNMR 2010 (Thanks for providing a raw table)
#    - Lee et al. PACSY, JBNMR 2012
# -----------------------------------------------------------------------------

import tkMessageBox

#Trans X-Pro shows strong NOEs between the two HD(PRO) and HA(X) and between the two HD(PRO) and NH(X).
#Cis X-Pro shows strong NOEs between the two HA(PRO) and HA(X) and between the two HA(PRO) and NH(X).
# That means, HD from Pro(i) to HA/H from Xaa(i-1) is strong -> Trans
#             HA from Pro(i) to HA/H from Xaa(i-1) is strong -> Cis

Clines="""170.35 0 1
170.85 2 0
171.35 2 0
171.85 5 1
172.35 6 5
172.85 17 8
173.35 29 3
173.85 48 7
174.35 59 9
174.85 89 17
175.35 122 15
175.85 147 12
176.35 169 7
176.85 176 3
177.35 130 3
177.85 88 0
178.35 74 0
178.85 52 0
179.35 33 0
179.85 11 0
180.35 4 0
180.85 0 0
181.35 0 0
181.85 1 0"""

CBlines="""26.75 1 0
27.25 2 0
27.75 4 0
28.25 9 0
28.75 5 0
29.25 8 0
29.75 12 0
30.25 23 1
30.75 72 2
31.25 130 1
31.75 260 2
32.25 474 5
32.75 363 6
33.25 167 13
33.75 51 14
34.25 14 17
34.75 10 26
35.25 5 14
35.75 1 7
36.25 3 3
36.75 1 0
37.25 0 1
37.75 0 1"""

CGlines="""21.25 1 0
21.75 0 0
22.25 0 0
22.75 1 0
23.25 0 1
23.75 0 4
24.25 6 8
24.75 6 19
25.25 6 9
25.75 21 0
26.25 45 1
26.75 129 2
27.25 273 0
27.75 240 1
28.25 99 0
28.75 43 0
29.25 14 0
29.75 4 0
30.25 2 0
30.75 0 0
31.25 0 0
31.75 4 0
32.25 1 0"""

Clist = Clines.split('\n')
CBlist = CBlines.split('\n')
CGlist = CGlines.split('\n')
C_init = float(Clist[0].split()[0]) - 0.25
CB_init = float(CBlist[0].split()[0]) - 0.25
CG_init = float(CGlist[0].split()[0]) - 0.25

C_list, CB_list, CG_list = [], [], []
transC_all, transCB_all, transCG_all = 0, 0, 0
cisC_all, cisCB_all, cisCG_all = 0, 0, 0

for line in Clist:
  sp = line.split()
  C_list.append( [float(sp[1]), float(sp[2])] )
  transC_all = transC_all + float(sp[1])
  cisC_all = cisC_all + float(sp[2])

for line in CBlist:
  sp = line.split()
  CB_list.append( [float(sp[1]), float(sp[2])] )
  transCB_all = transCB_all + float(sp[1])
  cisCB_all = cisCB_all + float(sp[2])

for line in CGlist:
  sp = line.split()
  CG_list.append( [float(sp[1]), float(sp[2])] )
  transCG_all = transCG_all + float(sp[1])
  cisCG_all = cisCG_all + float(sp[2])

# smoothing by -1, 0, 1
# returns trans_p, cis_p
def trans_cis_prob(shift, atom_type):
  if atom_type == 'C' or atom_type == 'CO':   
    curList, curInit, curTrans, curCis = C_list, C_init, 3.*transC_all, 3.*cisC_all
  elif atom_type == 'CB':                     
    curList, curInit, curTrans, curCis = CB_list, CB_init, 3.*transCB_all, 3.*cisCB_all
  elif atom_type == 'CG':                     
    curList, curInit, curTrans, curCis = CG_list, CG_init, 3.*transCG_all, 3.*cisCG_all

  idx = int((shift - curInit) / 0.5)
  if idx < 1: idx = 1
  if idx > len(curList)-2: idx = len(curList)-2

  trans_p = (curList[idx-1][0] + curList[idx][0] + curList[idx+1][0]) / curTrans
  cis_p = (curList[idx-1][1] + curList[idx][1] + curList[idx+1][1]) / curCis

  cur_all = trans_p + cis_p
  return trans_p / cur_all, cis_p / cur_all

def trans_cis_probs(shifts, atom_types):
  trans_p, cis_p = 1.0, 1.0
  for i in range(len(shifts)):
    shift, atom_type = shifts[i], atom_types[i]
    tp, cp = trans_cis_prob(shift, atom_type)
    trans_p = trans_p * tp
    cis_p = cis_p * cp
  all_p = trans_p + cis_p
  return trans_p / all_p, cis_p / all_p


def proline_cis_trans(session):
  trans_probs = map(lambda x: 1., range(1000))
  cis_probs = map(lambda x: 1., range(1000))
  prolines = map(lambda x: False, range(1000))
  for condition in session.project.condition_list():
    for resn in condition.resonance_list():
      if resn.group.symbol == 'P':
        if resn.group.number < 1 or resn.group.number > 999: continue
        prolines[resn.group.number] = True
        if resn.atom.name == 'C' or resn.atom.name == 'CO':
          t, c = trans_cis_prob(resn.frequency, 'C')
        elif resn.atom.name == 'CB':
          t, c = trans_cis_prob(resn.frequency, 'CB')
        elif resn.atom.name == 'CG':
          t, c = trans_cis_prob(resn.frequency, 'CG')
        else: continue
        trans_probs[resn.group.number] = trans_probs[resn.group.number] * t
        cis_probs[resn.group.number] = cis_probs[resn.group.number] * c
  
  msg = ''
  for i in range(1000):
    if not prolines[i]: continue
    t = trans_probs[i] / (trans_probs[i] + cis_probs[i])
    c = cis_probs[i] / (trans_probs[i] + cis_probs[i])
    if t > c: 
      st = 'trans-'
      p = t
    elif c > t: 
      st = 'cis-'
      p = c
    else: 
      st = 'unknown'
      p = t
    msg = msg + 'P%d (%s): %f\n' % (i, st, p)
  tkMessageBox.showinfo('Proline isomerization', msg)

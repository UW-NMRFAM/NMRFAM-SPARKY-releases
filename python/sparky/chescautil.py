# -----------------------------------------------------------------------------
# CHESCA UTILS
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: November 20, 2019
# 
#
# -----------------------------------------------------------------------------
# CITATION: TBA
#
# -----------------------------------------------------------------------------

import math

pairwise2d_prefix = """[GENERAL_START]
TITLE=CHESCA PAIRWISE SHIFT PLOT
XLABEL=$XLABEL N-H pseudoshift
YLABEL=$YLABEL N-H pseudoshift
XMIN=$XMIN
XMAX=$XMAX
YMIN=$YMIN
YMAX=$YMAX
XSCALE=FLOAT
YSCALE=FLOAT
WINDOW_WIDTH=700
WINDOW_HEIGHT=700
FIT_OPTION=LINEAR
DEFAULT_FIT=TRUE
[GENERAL_END]
[SERIES1_START]
NAME=INTERRESIDUE SHIFT CORRELATION
PLOTTYPE=DOT
XERROR=TRUE
YERROR=TRUE
COLORCOUNT=$COLORCOUNT
DATACOUNT=$DATACOUNT
$COLORLIST$DATALIST[SERIES1_END]"""
pairwise2d_color_list = ["255_0_0", "0_0_255", "0_255_0", "0_255_255", 
      "255_0_255", "255_255_0", "165_42_42", "42_165_42", 
      "42_42_165", "255_165_0", "255_0_165", "165_255_0",
      "0_255_165", "0_165_255", "165_0_255", "188_143_143",
      "143_188_143", "143_188_143"]

legend_prefix = """[GENERAL_START]
TITLE=CHESCA R PLOT LEGEND
XLABEL=R value
YLABEL= - / + 
XMIN=$XMIN
XMAX=1.00
YMIN=-1.3
YMAX=1.3
XSCALE=FLOAT
YSCALE=INT
WINDOW_WIDTH=700
WINDOW_HEIGHT=160
[GENERAL_END]
[SERIES1_START]
NAME=VALUES
PLOTTYPE=DOT
COLORCOUNT=100
DATACOUNT=100
$COLORLIST1$DATALIST1[SERIES1_END]
[SERIES2_START]
NAME=VALUES
PLOTTYPE=DOT
COLORCOUNT=100
DATACOUNT=100
$COLORLIST2$DATALIST2[SERIES2_END]"""

pymol_prefix = """select chesca-sparky, chesca and (($ID1/CA) or ($ID2/CA))
color cyan, chesca-sparky
center chesca-sparky
zoom center, 15
label chesca-sparky, "%s-%s[CA]:$CORR" % (resn, resi)
set label_distance_digits, 2
delete chesca_dist
distance chesca_dist, $ID1/CA, $ID2/CA
"""

pymol_multi_prefix = """select chesca-sparky_$ID1_$ID2, chesca and (($ID1/CA) or ($ID2/CA))
color cyan, chesca-sparky_$ID1_$ID2
center chesca-sparky_$ID1_$ID2
zoom center, 15
label chesca-sparky_$ID1_$ID2, "%s-%s[CA]:$CORR" % (resn, resi)
set label_distance_digits, 2
delete chesca_dist_$ID1_$ID2
distance chesca_dist_$ID1_$ID2, $ID1/CA, $ID2/CA
"""

pymol_prefix2 = """select chesca-cl-sparky, chesca and (n. CA and i. $IDS)
color magenta, chesca-cl-sparky
center chesca-cl-sparky
zoom center, 15
label
label chesca-cl-sparky, "%s-%s[CA]:$CORR" % (resn, resi)
"""

pymol_prefix3 = """select chesca-svd-sparky, chesca and (n. CA and i. $IDS)
color wheat, chesca-svd-sparky
center chesca-svd-sparky
zoom center, 15

label chesca-svd-sparky, "%s-%s[CA]:$PC" % (resn, resi)
"""

pymol_prefix4 = """select chespa-sparky_$ID, chespa and (n. CA and i. $ID)
color limon, chespa-sparky_$ID
center chespa-sparky_$ID
zoom center, 15
label chespa-sparky_$ID, "%s-%s[CA]:$FA,$COS" % (resn, resi)
show labels, chespa-sparky_$ID
"""


def ndp2d_prefix(sxmin, sxmax, symin, symax):
  prefix = """[GENERAL_START]
TITLE=CHESCA R PLOT
XLABEL=Residue number
YLABEL=Residue number
XMIN=%d
XMAX=%d
YMIN=%d
YMAX=%d
XSCALE=INT
YSCALE=INT
WINDOW_WIDTH=700
WINDOW_HEIGHT=700
[GENERAL_END]
[SERIES1_START]
NAME=CORRELATED
PLOTTYPE=DOT
COLORCOUNT=$COLORCOUNT
DATACOUNT=$DATACOUNT
$COLORLIST$DATALIST[SERIES1_END]""" % (sxmin, sxmax, symin, symax)
  return prefix

def calc_pseudo_ppm(nscale, frq1, frq2):
  return math.sqrt( (nscale * frq1) ** 2.0 + \
            frq2 ** 2.0)

def calc_pseudo_ppm_difference(nscale, frq1, frq2):
  n_ppm1 = max(frq1)
  h_ppm1 = min(frq1)
  n_ppm2 = max(frq2)
  h_ppm2 = min(frq2)
  diff = math.sqrt( (n_ppm1-n_ppm2) ** 2 * nscale ** 2 + \
            (h_ppm1-h_ppm2) ** 2 )
  return diff

# frqMN: M->bound state, N->mutation state
# vecA -> frq21 - frq11
# vecB -> frq12 - frq11
def calc_cosine_theta(nscale, frq11, frq12, frq21):
  a1 = nscale*(frq12[0]-frq11[0])
  a2 = frq12[1]-frq11[1]
  b1 = nscale*(frq21[0]-frq11[0])
  b2 = frq21[1]-frq11[1]
  dist_a = calc_pseudo_ppm_difference(nscale, frq11, frq12)
  dist_b = calc_pseudo_ppm_difference(nscale, frq11, frq21)
  cos_theta = (a1*b1+a2*b2) / (dist_a * dist_b)
  return cos_theta

def calc_theta(nscale, frq11, frq12, frq21):
  theta = calc_cosine_theta(nscale, frq11, frq12, frq21)
  return math.acos(theta)

def calc_fractional_shift(nscale, frq11, frq12, frq21):
  # X = |vec(A)|*cos(theta)/|vec(B)|
  absA = calc_pseudo_ppm_difference(nscale, frq12, frq11)
  absB = calc_pseudo_ppm_difference(nscale, frq21, frq11)
  cos_theta = calc_cosine_theta(nscale, frq11, frq12, frq21)
  X = absA*cos_theta / absB
  return X
# calculate chespa using three peaks
# returns difference, X, cos(theta) 
def calc_chespa_per_residue(nscale, frq11, frq12, frq21):
  diff = calc_pseudo_ppm_difference(nscale, frq11, frq12)
  X = calc_fractional_shift(nscale, frq11, frq12, frq21)
  cos_theta = calc_cosine_theta(nscale, frq11, frq12, frq21)
  return diff, X, cos_theta

def ndp_2d_chespa_prefix(sxmin, sxmax, symin, symax, title, label):
  prefix = """[GENERAL_START]
TITLE=%s
XLABEL=Residue number
YLABEL=%s
XMIN=%d
XMAX=%d
YMIN=%f
YMAX=%f
XSCALE=INT
YSCALE=FLOAT
[GENERAL_END]
[SERIES1_START]
NAME=BAR PLOT
PLOTTYPE=BAR
COLORCOUNT=3
DATACOUNT=$DATACOUNT
COLOR_1=%d,%d,%f,%f,0_0_125
COLOR_2=%d,%d,-9999,%f,255_0_0
COLOR_3=%d,%d,%f,9999,255_0_0
$DATALIST[SERIES1_END]""" % (title, label, sxmin, sxmax, symin, symax,\
                    sxmin, sxmax, symin, symax, 
                    sxmin, sxmax, symin,
                    sxmin, sxmax, symax)
  return prefix

def ndp2d_chespa_ppm_prefix(sxmin, sxmax, symin, symax, 
          xtitle='CHESPA PERTURBATION PLOT', ytitle='|Wt. - Mut.| (ppm)'):
  return ndp_2d_chespa_prefix(sxmin, sxmax, symin, symax, \
              xtitle,ytitle)

def ndp2d_chespa_reference_ppm_prefix(sxmin, sxmax, symin, symax, 
          xtitle='CHESPA REFERENCE PLOT', ytitle='|Apo. - Holo.| (ppm)'):
  return ndp_2d_chespa_prefix(sxmin, sxmax, symin, symax, \
              xtitle,ytitle)

def ndp2d_chespa_fractional_shift_prefix(sxmin, sxmax, symin, symax, 
        xtitle='CHESPA FRACTIONAL ACTIVITY PLOT', ytitle='X (Fractional Activ.)'):
  return ndp_2d_chespa_prefix(sxmin, sxmax, symin, symax, \
              xtitle,ytitle)

def ndp2d_chespa_cosine_theta_prefix(sxmin, sxmax, symin, symax, 
        xtitle='CHESPA PROJECTION ANGLE PLOT',ytitle='cos(theta)'):
  return ndp_2d_chespa_prefix(sxmin, sxmax, symin, symax, \
              xtitle,ytitle)

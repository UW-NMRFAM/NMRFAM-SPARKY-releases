# ---------------------------------------------------------------------------
# Amino acid chemical shift statistics from BioMagResBank
#
# Statistics Calculated for Selected Chemical Shifts from Atoms in the
# 20 Common Amino Acids
#
# BMRB Entries not included in the calculations for this table contained
# chemical shifts outside eight standard deviations from the mean
# calculated for the full BMRB database or a chemical shift for at least
# one carbon bound proton that was greater than 10ppm or was less than
# -2.5ppm.  These criteria were used to eliminate from the calculations
# chemical shifts from paramagnetic proteins, from proteins with
# aromatic prosthetic groups, and from entries where unusual chemical
# shift referencing was used.  Of the 145,398 possible chemical shifts
# in the BMRB database, 123,360 were included in calculating this table.
#
# -----------------------------------------------------------------------------
# BMRB statistics updates -
# -----------------------------------------------------------------------------
# 03-01-2018
# Now 6,028,865 chemical shifts included from 8,042,265
# Diamagnetics only. Additional: ASP HD2, GLU HE2
# ----------------------------------------------------------------------------- 
# 02-09-2017
# Now 5,702,216 chemical shifts included from 7,592,598
# Diamagnetics only. Additional: ASP HD2, GLU HE2
# ----------------------------------------------------------------------------- 
# by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last Update: Dec 12, 2018
# 
# -----------------------------------------------------------------------------
import string
import sys
import atomnames
from math import erf, sqrt
import math

# -----------------------------------------------------------------------------
#
bmrb_lines = """
ALA     H        H        56541        3.53        12.11       8.19       0.58       
ALA     HA       H        39648        0.87         6.51       4.24       0.43       
ALA     HB       H        37420       -0.83         3.12       1.36       0.24       
ALA     C        C        37173      164.48       187.20     177.81       2.07       
ALA     CA       C        50536       39.92        67.02      53.18       1.93       
ALA     CB       C        47380        6.61        43.14      18.97       1.78       
ALA     N        N        53743       98.05       142.81     123.29       3.46       

ARG     H        H        37394        3.57        12.69       8.23       0.61       
ARG     HA       H        26828        1.29         6.62       4.29       0.45       
ARG     HB2      H        24197       -0.61         3.74       1.80       0.26       
ARG     HB3      H        22911       -0.74         3.74       1.76       0.27       
ARG     HG2      H        21590       -0.64         3.51       1.57       0.27       
ARG     HG3      H        20028       -0.74         3.51       1.55       0.28       
ARG     HD2      H        21175        1.04         4.69       3.12       0.23       
ARG     HD3      H        19319        0.85         4.69       3.10       0.25       
ARG     HE       H        6441         2.20        11.88       7.36       0.58       
ARG     HH11     H        570          5.88        10.07       6.90       0.46       
ARG     HH12     H        439          5.92        10.73       6.86       0.49       
ARG     HH21     H        498          4.85        11.35       6.82       0.49       
ARG     HH22     H        404          5.92        10.19       6.83       0.49       
ARG     C        C        23203      167.44       184.51     176.48       2.00       
ARG     CA       C        32397       35.70        67.98      56.81       2.30       
ARG     CB       C        30041       20.78        42.50      30.64       1.81       
ARG     CG       C        18011       18.22        49.39      27.22       1.20       
ARG     CD       C        18209       27.12        50.88      43.15       0.93       
ARG     CZ       C        471        113.28       179.92     160.03       3.84       
ARG     N        N        34489      102.78       137.60     120.80       3.63       
ARG     NE       N        3865        67.00        99.81      84.59       1.61       
ARG     NH1      N        114         67.60        87.82      74.41       5.25       
ARG     NH2      N        106         69.26        87.83      72.75       3.00       

ASP     H        H        44374        4.06        12.68       8.30       0.56       
ASP     HA       H        31070        2.33         6.67       4.58       0.31       
ASP     HB2      H        28813       -0.39         4.60       2.71       0.26       
ASP     HB3      H        27659       -0.23         4.58       2.66       0.27       
ASP     HD2      H        2            4.65         9.29       6.97       3.28       
ASP     C        C        28484      166.80       182.70     176.45       1.71       
ASP     CA       C        39347       41.11        67.17      54.70       2.02       
ASP     CB       C        37035       26.50        58.51      40.87       1.61       
ASP     CG       C        485        170.72       186.50     179.31       1.82       
ASP     N        N        42363      101.90       143.52     120.68       3.79       

ASN     H        H        31170        3.46        12.68       8.32       0.61       
ASN     HA       H        22410        2.04         6.60       4.66       0.35       
ASN     HB2      H        20873        0.22         4.47       2.80       0.31       
ASN     HB3      H        20105       -0.07         4.77       2.75       0.33       
ASN     HD21     H        15433        2.06        10.92       7.32       0.48       
ASN     HD22     H        15211        2.58        10.92       7.15       0.50       
ASN     C        C        19802      167.75       185.30     175.30       1.76       
ASN     CA       C        27590       41.20        66.21      53.56       1.86       
ASN     CB       C        26026       26.45        57.35      38.70       1.66       
ASN     CG       C        1744       166.40       183.80     176.79       1.38       
ASN     N        N        29035      101.71       137.49     118.91       3.92       
ASN     ND2      N        13217       99.40       134.50     112.76       2.27       

CYS     H        H        15674        4.38        12.66       8.38       0.68       
CYS     HA       H        12986        1.64         6.45       4.65       0.54       
CYS     HB2      H        12492       -0.54         4.72       2.95       0.44       
CYS     HB3      H        12176       -0.83         4.77       2.89       0.45       
CYS     HG       H        148         -1.83         7.39       1.92       1.22       
CYS     C        C        7693       166.73       187.59     174.91       2.04       
CYS     CA       C        11131       41.51        68.07      58.15       3.43       
CYS     CB       C        10538       17.99        63.89      33.07       6.36       
CYS     N        N        12083      100.48       138.68     120.12       4.48       

GLU     H        H        58026        4.29        12.69       8.33       0.58       
GLU     HA       H        40906        1.39         6.32       4.24       0.40       
GLU     HB2      H        36773        0.34         3.37       2.02       0.21       
GLU     HB3      H        34567        0.27         3.47       2.00       0.21       
GLU     HG2      H        33917        0.53         3.77       2.27       0.21       
GLU     HG3      H        31607        0.56         3.83       2.25       0.21       
GLU     HE2      H        3            2.73         2.93       2.82       0.10       
GLU     C        C        38087      166.80       183.52     176.94       1.90       
GLU     CA       C        51729       44.35        70.38      57.35       2.07       
GLU     CB       C        48047       18.36        49.56      29.96       1.70       
GLU     CG       C        30133       25.06        54.83      36.11       1.20       
GLU     CD       C        552        173.41       189.46     182.27       2.46       
GLU     N        N        55698      101.34       138.60     120.72       3.44       

GLN     H        H        32102        3.51        12.22       8.22       0.58       
GLN     HA       H        22728        1.57         6.44       4.26       0.42       
GLN     HB2      H        20536       -0.14         4.00       2.04       0.25       
GLN     HB3      H        19566       -0.57         4.04       2.01       0.27       
GLN     HG2      H        19128       -0.11         4.44       2.31       0.26       
GLN     HG3      H        17702       -0.41         4.44       2.29       0.28       
GLN     HE21     H        14214        3.39        11.11       7.22       0.44       
GLN     HE22     H        14141        3.59        10.35       7.04       0.43       
GLN     C        C        20944      168.09       185.31     176.36       1.91       
GLN     CA       C        28907       43.45        66.60      56.60       2.10       
GLN     CB       C        26932       18.43        43.65      29.16       1.80       
GLN     CG       C        16890       21.64        51.08      33.78       1.11       
GLN     CD       C        1661       171.37       183.54     179.73       1.21       
GLN     N        N        30573      103.88       139.55     119.93       3.54       
GLN     NE2      N        12721       92.49       133.30     111.86       1.68       

GLY     H        H        55926        3.34        12.22       8.33       0.63       
GLY     HA2      H        38583        0.84         6.98       3.96       0.37       
GLY     HA3      H        36672        0.74         6.98       3.90       0.37       
GLY     C        C        36032      163.27       184.89     173.91       1.84       
GLY     CA       C        50066       33.15        60.91      45.37       1.30       
GLY     N        N        52274       93.60       162.19     109.59       3.68       

HIS     H        H        15735        3.97        12.39       8.25       0.67       
HIS     HA       H        11582        1.93         8.90       4.60       0.43       
HIS     HB2      H        10709       -0.04         8.70       3.10       0.35       
HIS     HB3      H        10385       -0.39         8.70       3.05       0.37       
HIS     HD1      H        477          2.73        17.20       8.58       2.45       
HIS     HD2      H        7471         3.65         9.42       7.00       0.41       
HIS     HE1      H        5833         3.21        10.88       7.96       0.48       
HIS     HE2      H        185          6.57        16.53       9.62       2.40       
HIS     C        C        10106      166.90       183.12     175.26       1.94       
HIS     CA       C        14416       43.31        77.56      56.51       2.31       
HIS     CB       C        13463       18.75        54.90      30.24       2.10       
HIS     CG       C        115        117.54       139.56     132.01       3.24       
HIS     CD2      C        4929       110.52       159.95     120.39       3.36       
HIS     CE1      C        3779       104.67       145.42     137.64       2.26       
HIS     N        N        14706      103.99       136.48     119.70       4.02       
HIS     ND1      N        251        164.31       229.14     193.57      18.57       
HIS     NE2      N        259        161.10       226.76     184.54      16.46       

ILE     H        H        39166        3.75        11.87       8.26       0.68       
ILE     HA       H        27755        1.32         6.36       4.16       0.55       
ILE     HB       H        26014       -1.28         3.87       1.78       0.29       
ILE     HG12     H        23493       -2.12         2.69       1.28       0.40       
ILE     HG13     H        22589       -2.07         2.99       1.20       0.41       
ILE     HG2      H        24722       -1.47         2.20       0.78       0.27       
ILE     HD1      H        25318       -1.47         2.82       0.68       0.28       
ILE     C        C        25476      166.40       187.55     175.93       1.90       
ILE     CA       C        34965       43.84        71.86      61.68       2.68       
ILE     CB       C        32528       18.10        51.88      38.57       2.00       
ILE     CG1      C        20647        8.77        42.09      27.74       1.70       
ILE     CG2      C        21871        3.45        37.01      17.53       1.34       
ILE     CD1      C        22392        4.94        29.60      13.41       1.66       
ILE     N        N        37186       99.00       138.12     121.42       4.22       

LEU     H        H        65327        4.08        13.22       8.22       0.63       
LEU     HA       H        45905        1.72         6.42       4.30       0.46       
LEU     HB2      H        42010       -1.21         4.13       1.61       0.34       
LEU     HB3      H        40217       -1.41         3.23       1.52       0.36       
LEU     HG       H        36970       -1.06         3.90       1.51       0.33       
LEU     HD1      H        41825       -1.73         2.36       0.75       0.27       
LEU     HD2      H        40164       -1.74         2.15       0.73       0.28       
LEU     C        C        42360      166.22       189.78     177.07       1.93       
LEU     CA       C        58131       42.69        67.88      55.69       2.11       
LEU     CB       C        54177       26.40        53.70      42.25       1.85       
LEU     CG       C        32159       15.30        38.62      26.78       1.10       
LEU     CD1      C        35845       10.95        36.85      24.66       1.59       
LEU     CD2      C        34158        9.86        30.40      24.08       1.69       
LEU     N        N        61838       98.56       177.62     121.83       3.86       

LYS     H        H        54570        4.11        12.03       8.18       0.60       
LYS     HA       H        39423        0.68         6.17       4.26       0.43       
LYS     HB2      H        35066       -0.25         3.82       1.78       0.24       
LYS     HB3      H        33138       -0.45         3.82       1.75       0.26       
LYS     HG2      H        31689       -0.77         3.13       1.37       0.25       
LYS     HG3      H        29274       -0.87         3.05       1.35       0.27       
LYS     HD2      H        28120       -1.68         3.19       1.61       0.21       
LYS     HD3      H        25389       -0.57         3.19       1.60       0.21       
LYS     HE2      H        27822        1.23         4.43       2.91       0.19       
LYS     HE3      H        24592        1.17         4.55       2.91       0.20       
LYS     HZ       H        982          1.95         9.90       7.38       0.67       
LYS     C        C        34402      166.63       185.00     176.72       1.91       
LYS     CA       C        47464       40.73        65.87      56.98       2.17       
LYS     CB       C        44044       21.19        46.60      32.77       1.77       
LYS     CG       C        27144       16.85        40.50      24.90       1.13       
LYS     CD       C        25593       15.37        42.70      28.96       1.11       
LYS     CE       C        24699       25.24        56.00      41.89       0.88       
LYS     N        N        50855      101.10       140.30     121.03       3.70       
LYS     NZ       N        69          29.48        35.90      33.07       1.15       

MET     H        H        15593        4.87        12.46       8.25       0.58       
MET     HA       H        11438        1.13         6.35       4.39       0.46       
MET     HB2      H        10186       -1.05         4.07       2.02       0.33       
MET     HB3      H        9569        -0.99         3.47       1.99       0.34       
MET     HG2      H        9313        -0.42         4.40       2.42       0.35       
MET     HG3      H        8807        -0.47         4.24       2.39       0.38       
MET     HE       H        6835        -0.71         8.38       1.89       0.40       
MET     C        C        10376      167.40       183.16     176.26       2.05       
MET     CA       C        14566       43.28        66.86      56.16       2.20       
MET     CB       C        13401       20.36        46.46      32.93       2.18       
MET     CG       C        7838        15.94        51.70      32.03       1.28       
MET     CE       C        6141        10.50        44.10      17.10       1.67       
MET     N        N        14935      102.80       138.55     120.11       3.48       

PHE     H        H        27703        3.55        12.18       8.34       0.71       
PHE     HA       H        19249        1.78         6.87       4.61       0.56       
PHE     HB2      H        17826        0.16         4.46       3.00       0.37       
PHE     HB3      H        17413       -0.21         4.69       2.94       0.39       
PHE     HD1      H        14789        4.47         8.15       7.06       0.31       
PHE     HD2      H        12663        4.47         8.15       7.06       0.31       
PHE     HE1      H        12814        4.38         8.80       7.08       0.31       
PHE     HE2      H        11123        4.38         8.80       7.08       0.31       
PHE     HZ       H        9046         4.32         9.50       6.99       0.41       
PHE     C        C        17711      166.85       184.93     175.50       1.97       
PHE     CA       C        24358       36.03        69.82      58.14       2.57       
PHE     CB       C        22729       25.52        55.62      39.93       2.06       
PHE     CG       C        230        127.24       152.84     138.45       2.83       
PHE     CD1      C        8777       116.95       143.16     131.58       1.21       
PHE     CD2      C        6474       115.55       138.70     131.59       1.21       
PHE     CE1      C        7611       114.75       139.56     130.74       1.31       
PHE     CE2      C        5616       114.70       139.70     130.77       1.20       
PHE     CZ       C        5822       115.10       139.13     129.22       1.48       
PHE     N        N        26105      102.20       139.02     120.38       4.13       

PRO     HA       H        22254        1.04         8.08       4.39       0.33       
PRO     HB2      H        20550       -0.75         4.59       2.08       0.35       
PRO     HB3      H        19955       -0.58         3.79       2.00       0.35       
PRO     HG2      H        18430       -0.77         4.42       1.93       0.31       
PRO     HG3      H        17111       -0.73         4.42       1.90       0.32       
PRO     HD2      H        18857        0.63         5.36       3.65       0.35       
PRO     HD3      H        18199        0.34         5.36       3.62       0.38       
PRO     C        C        18984      168.38       182.84     176.76       1.48       
PRO     CA       C        27045       48.56        72.28      63.35       1.51       
PRO     CB       C        25195       20.91        56.76      31.85       1.18       
PRO     CG       C        16493       18.28        50.75      27.20       1.10       
PRO     CD       C        16470       26.92        58.81      50.34       1.05       
PRO     N        N        1049       110.49       145.26     135.20       5.65       

SER     H        H        47747        3.76        12.52       8.28       0.58       
SER     HA       H        34403        1.28         6.85       4.47       0.40       
SER     HB2      H        31327        1.70         5.45       3.87       0.25       
SER     HB3      H        29052        1.55         5.45       3.85       0.27       
SER     HG       H        520          0.13         8.97       5.37       1.07       
SER     C        C        31087      164.47       197.10     174.66       1.72       
SER     CA       C        43383       45.13        73.19      58.74       2.07       
SER     CB       C        40017       31.40        76.39      63.80       1.51       
SER     N        N        44923       95.97       133.68     116.28       3.49       

THR     H        H        42051        5.32        11.80       8.24       0.62       
THR     HA       H        29789        1.65         7.47       4.45       0.47       
THR     HB       H        27009        0.92         8.35       4.16       0.32       
THR     HG1      H        899         -1.78         9.01       5.10       1.29       
THR     HG2      H        26737       -0.97         3.28       1.14       0.22       
THR     C        C        26795      165.50       184.43     174.58       1.72       
THR     CA       C        37136       48.01        72.80      62.25       2.58       
THR     CB       C        34255       29.97        81.53      69.71       1.72       
THR     CG2      C        22289       11.70        36.73      21.55       1.10       
THR     N        N        39728       95.77       138.27     115.35       4.72       

TRP     H        H        8830         5.16        11.76       8.27       0.77       
TRP     HA       H        6111         2.24         6.58       4.66       0.52       
TRP     HB2      H        5738         0.68         4.54       3.19       0.34       
TRP     HB3      H        5573         0.26         4.44       3.12       0.36       
TRP     HD1      H        5096         4.60         8.93       7.14       0.34       
TRP     HE1      H        5650         5.12        14.39      10.08       0.64       
TRP     HE3      H        4410         4.89         9.95       7.32       0.41       
TRP     HZ2      H        4754         4.66         8.56       7.28       0.32       
TRP     HZ3      H        4267         3.88         8.90       6.87       0.37       
TRP     HH2      H        4379         4.37        10.17       6.98       0.36       
TRP     C        C        5317       168.17       182.60     176.21       1.97       
TRP     CA       C        7414        43.50        81.00      57.74       2.54       
TRP     CB       C        6902        18.63        52.30      29.97       1.99       
TRP     CG       C        139        107.50       116.53     111.06       1.81       
TRP     CD1      C        3164       108.45       135.60     126.56       1.86       
TRP     CD2      C        111        120.00       132.62     127.79       1.87       
TRP     CE2      C        110        113.89       177.71     138.07       7.16       
TRP     CE3      C        2644        93.34       137.60     120.47       1.83       
TRP     CZ2      C        3020        81.81       134.70     114.26       1.45       
TRP     CZ3      C        2684        98.61       138.39     121.37       1.60       
TRP     CH2      C        2822        91.62       131.54     123.81       1.58       
TRP     N        N        7977       101.97       138.11     121.59       4.07       
TRP     NE1      N        4534       106.00       144.36     129.28       2.07       

TYR     H        H        23419        4.16        12.34       8.30       0.72       
TYR     HA       H        16536        1.19         6.83       4.60       0.55       
TYR     HB2      H        15261       -0.49         4.70       2.90       0.37       
TYR     HB3      H        14910       -0.19         4.70       2.84       0.39       
TYR     HD1      H        13176        4.68         8.54       6.93       0.29       
TYR     HD2      H        11466        4.43         8.54       6.93       0.29       
TYR     HE1      H        12489        4.58         7.85       6.70       0.22       
TYR     HE2      H        10963        4.56         8.50       6.70       0.23       
TYR     HH       H        229         -0.79        13.75       9.12       1.61       
TYR     C        C        14470      167.86       184.78     175.51       1.95       
TYR     CA       C        20188       44.64        69.56      58.19       2.49       
TYR     CB       C        18652       25.32        57.73      39.27       2.14       
TYR     CG       C        204        117.70       144.30     129.59       2.48       
TYR     CD1      C        7872       115.30       141.57     132.73       1.34       
TYR     CD2      C        5615       113.00       139.47     132.70       1.49       
TYR     CE1      C        7797       110.70       137.42     117.94       1.26       
TYR     CE2      C        5543       106.55       135.82     117.91       1.24       
TYR     CZ       C        154        153.54       160.45     156.82       1.48       
TYR     N        N        21563      100.09       144.96     120.49       4.09       

VAL     H        H        51418        3.98        12.59       8.28       0.66       
VAL     HA       H        36447        0.97         6.30       4.16       0.57       
VAL     HB       H        33739       -1.24         3.76       1.98       0.31       
VAL     HG1      H        33386       -1.13         2.57       0.83       0.26       
VAL     HG2      H        32688       -2.32         3.32       0.80       0.28       
VAL     C        C        33724      165.65       183.95     175.71       1.85       
VAL     CA       C        45878       44.98        70.34      62.57       2.84       
VAL     CB       C        42282       18.97        45.33      32.70       1.78       
VAL     CG1      C        28841       12.07        32.27      21.52       1.36       
VAL     CG2      C        27806       11.38        33.12      21.29       1.53       
VAL     N        N        49110       97.22       143.29     121.10       4.44        
"""
stat_list = bmrb_lines.split('\n')
stat_list2 = []
for i in range(len(stat_list)):   
  stat_list[i] = stat_list[i].strip()
  if stat_list[i] != '': stat_list2.append(stat_list[i])
stat_lines = tuple(stat_list2)
stat_list = []
stat_list2 = []
# -----------------------------------------------------------------------------
# make atom sets
atom_list = []
cur_a = 'X'
for line in stat_lines:
  fields = string.split(line)
  gsym = atomnames.aaa_to_a[fields[0]]
  if gsym != cur_a:
    cur_list = [gsym, []]
    atom_list.append(cur_list)
    cur_a = gsym
  aname = fields[1]
  cur_list[1].append(aname)
atom_dict = dict(atom_list)
atom_list = []
# -----------------------------------------------------------------------------
#
def get_zscore(value, mean, dev):
  if dev == 0:
    return 0
  return (value - mean) / dev

def z2p(z):
  return 0.5 * (1+erf(z/sqrt(2)))

def get_pvalue(value, mean, dev):
  zvalue = abs(get_zscore(value, mean, dev)) * -1.
  pvalue = z2p(zvalue) * 2.
  return pvalue
  
# alternative approach
def normpdf(x, mean, sd):
  var = float(sd)**2
  pi = 3.1415926
  denom = (2*pi*var)**.5
  num = math.exp(-(float(x)-float(mean))**2/(2*var))
  return num/denom
# -----------------------------------------------------------------------------
#
class atom_stats:

  def __init__(self, gsym, aname, nucleus, count, fmin, fmax, fave, fdev):

    self.group_symbol = gsym
    self.atom_name = aname
    self.nucleus = nucleus
    self.count = count
    self.minimum_shift = fmin
    self.maximum_shift = fmax
    self.average_shift = fave
    self.shift_deviation = fdev
# -----------------------------------------------------------------------------
#
def get_atoms_by_sequence(seq):
  atoms = []
  all_atoms = atomnames.protein_atoms_by_group_2[seq]
  for atm in all_atoms:
    ast = atom_statistics(seq, atm)
    if ast == None: continue  
    atoms.append(atm)
  return atoms
# -----------------------------------------------------------------------------
#
def atom_statistics(group_symbol, atom_name):

  ast = atom_statistics_table()
  key = (group_symbol, atom_name)
  if ast.has_key(key):
    return ast[key]
  
  return None

# -----------------------------------------------------------------------------
#
atom_stat_table = None
def atom_statistics_table():
  
  global atom_stat_table
  if atom_stat_table == None:
    atom_stat_table = {}
    nucleus_translation = { 'H':'1H', 'N':'15N', 'C':'13C' }
    for line in stat_lines:
      fields = string.split(line)
      gsym = atomnames.aaa_to_a[fields[0]]
      aname = fields[1]
      nucleus = nucleus_translation[fields[2]]
      count = string.atoi(fields[3])
      fmin = string.atof(fields[4])
      fmax = string.atof(fields[5])
      fave = string.atof(fields[6])
      fdev = string.atof(fields[7])
      atom_stat_table[(gsym, aname)] = \
        atom_stats(gsym, aname, nucleus, count, fmin, fmax, fave, fdev)

  return atom_stat_table


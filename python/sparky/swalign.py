# -----------------------------------------------------------------------------
# Smith-Waterman Alignment Implementation for NMRFAM-SPARKY
# -----------------------------------------------------------------------------
#
# Developed by Woonghee Lee
# e-mail: whlee@nmrfam.wisc.edu
# National Magnetic Resonance Facilities at Madison
# Department of Bichemistry, University of Wisconsin at Madison
#
# Last updated: June 27, 2019
#
#
# -----------------------------------------------------------------------------
# CITATION:
#
# -----------------------------------------------------------------------------

# environmental variables

m_gap = -1
m_singlea = 'ARNDCQEGHILKMFPSTWYVX'
m_ppiBlosum62=[
    [ 4,-1,-2,-2, 0,-1,-1, 0,-2,-1,-1,-1,-1,-2,-1, 1, 0,-3,-2, 0, -1],
    [-1, 5, 0,-2,-3, 1, 0,-2, 0,-3,-2, 2,-1,-3,-2,-1,-1,-3,-2,-3, -1],
    [-2, 0, 6, 1,-3, 0, 0, 0, 1,-3,-3, 0,-2,-3,-2, 1, 0,-4,-2,-3, -1],
    [-2,-2, 1, 6,-3, 0, 2,-1,-1,-3,-4,-1,-3,-3,-1, 0,-1,-4,-3,-3, -1],
    [ 0,-3,-3,-3, 9,-3,-4,-3,-3,-1,-1,-3,-1,-2,-3,-1,-1,-2,-2,-1, -1],
    [-1, 1, 0, 0,-3, 5, 2,-2, 0,-3,-2, 1, 0,-3,-1, 0,-1,-2,-1,-2, -1],
    [-1, 0, 0, 2,-4, 2, 5,-2, 0,-3,-3, 1,-2,-3,-1, 0,-1,-3,-2,-2, -1],
    [ 0,-2, 0,-1,-3,-2,-2, 6,-2,-4,-4,-2,-3,-3,-2, 0,-2,-2,-3,-3, -1],
    [-2, 0, 1,-1,-3,-0, 0,-2, 8,-3,-3,-1,-2,-1,-2,-1,-2,-2, 2,-3, -1],
    [-1,-3,-3,-3,-1,-3,-3,-4,-3, 4, 2,-3, 1, 0,-3,-2,-1,-3,-1, 3, -1],
    [-1,-2,-3,-4,-1,-2,-3,-4,-3, 2, 4,-2, 2, 0,-3,-2,-1,-2,-1, 1, -1],
    [-1, 2, 0,-1,-3, 1, 1,-2,-1,-3,-2, 5,-1,-3,-1, 0,-1,-3,-2,-2, -1],
    [-1,-1,-2,-3,-1, 0,-2,-3,-2, 1, 2,-1, 5, 0,-2,-1,-1,-1,-1, 1, -1],
    [-2,-3,-3,-3,-2,-3,-3,-3,-1, 0, 0,-3, 0, 6,-4,-2,-2, 1, 3,-1, -1],
    [-1,-2,-2,-1,-3,-1,-1,-2,-2,-3,-3,-1,-2,-4, 7,-1,-1,-4,-3,-2, -1],
    [ 1,-1, 1, 0,-1, 0, 0, 0,-1,-2,-2, 0,-1,-2,-1, 4, 1,-3,-2,-2, -1],
    [ 0,-1, 0,-1,-1,-1,-1,-2,-2,-1,-1,-1,-1,-2,-1, 1, 5,-2,-2, 0, -1],
    [-3,-3,-4,-4,-2,-2,-3,-2,-2,-3,-2,-3,-1, 1,-4,-3,-2,11, 2,-3, -1],
    [-2,-2,-2,-3,-2,-1,-2,-3, 2,-1,-1,-2,-1, 3,-3,-2,-2, 2, 7,-1, -1],
    [ 0,-3,-3,-3,-1,-2,-2,-3,-3, 3, 1,-2, 1,-1,-2,-2, 0,-3,-1, 4, -1],
    [-1,-1,-1,-1,-1,-1,-1,-1,-1, 1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,  0],]

def get_score(a1, a2):
  i1 = m_singlea.index(a1)
  i2 = m_singlea.index(a2)
  return m_ppiBlosum62[i1][i2]

def compresslist(lt):
  a = ''
  for l in lt:
    a = a + l
  return a

def reverse(string):
    string = "".join(reversed(string))
    return string

def traceback(s1, s2, scoremat):
  m = len(s1)+1
  n = len(s2)+1
  i = m-1
  j = n-1
  k = 0

  c = list(map(lambda x: ' ', range(m + n + 1)))
  d = list(map(lambda x: ' ', range(m + n + 1)))

  # we go global so skip this which is for local traceback
  #swmax = 2.2250738585072013830902327173324040642192159804623318306 * 10**-308
  #for l in range(0, m):
  #  for n in range(0, m):
  #    if scoremat[l][n][0] > swmax:
  #      i = l
  #      j = n

  o, p = -1, -1
  if scoremat[i][j][1] != 0 and scoremat[i][j][2] != 0:
    while i > 0 or j > 0:
      new_i = scoremat[i][j][1]
      new_j = scoremat[i][j][2]

      if new_i < i:
        c[k] = s1[i-1]
        o = i-1
      else:
        c[k] = '-'

      if new_j < j:
        d[k] = s2[j-1]
        p = j-1
      else:
        d[k] = '-'

      k = k+1
      i = new_i
      j = new_j
  e = compresslist(c)
  f = compresslist(d)
  return reverse(e).strip(), reverse(f).strip(), k, o, p # matchseq1, matchseq2, new length, seqnum1 (from zero), seqnum2 (from zero)

def max_blosum(seq):
  sum_score = 0
  for s in seq:
    score = get_score(s, s)
    sum_score = sum_score + score
  return sum_score

def swalign(seq1, seq2):
  s1 = seq1.upper() # support lower cases
  s2 = seq2.upper() # support lower cases
  c1 = len(s1)
  c2 = len(s2)

  # make score and prev matrix
  scoremat = list(map(lambda x: list(map(lambda y: [0,0,0], range(c2+1))),
                    range(c1+1)))

  # initialize
  for i in range(1, c1+1):
    scoremat[i][0][1] = i-1
  for i in range(1, c2+1):
    scoremat[0][i][2] = i-1

  # score match
  for i in range(1, c1+1):
    for j in range(1, c2+1):
      score = get_score(s1[i-1], s2[j-1])
      scoremat[i][j][0] = 2.2250738585072013830902327173324040642192159804623318306 * 10**-308 # DBL_MIN
      scoremat[i][j][1] = 0
      scoremat[i][j][2] = 0

      for k in range(0, 2):
        for l in range(0, 2):
          if k == 0 and l == 0: continue
          elif k > 0 and l > 0:
            val = score
          elif k > 0 or l > 0:
            if (i == c1 and k == 0) or (j == c2 and l == 0): val = 0
            else: val = m_gap
          else:
            pass

          val = val + scoremat[i-k][j-l][0]
          if val > scoremat[i][j][0]:
            scoremat[i][j][0] = val
            scoremat[i][j][1] = i-k
            scoremat[i][j][2] = j-l
  return traceback(s1, s2, scoremat)

def do_swalign(seq1, num1, seq2, num2):
  matchseq1, matchseq2, matchlen, matchidx1, matchidx2 = swalign(seq1, seq2)
  list1 = list(map(lambda x: -9999, range(len(seq1)+len(seq2)+num1+num2)))
  list2 = list(map(lambda x: -9999, range(len(seq1)+len(seq2)+num1+num2)))

  dict_list1 = []
  dict_list2 = []

  mseq1 = matchseq1.replace('-', '')
  mseq2 = matchseq2.replace('-', '')
  start1 = seq1.find(mseq1)
  start2 = seq2.find(mseq2)

  iCurIdx = num1 + start1
  for i in range(len(matchseq1)):
    if matchseq1[i] != '-':
      list1[iCurIdx] = i
      #list1[iCurIdx] = start1 + i
      iCurIdx = iCurIdx + 1

  iCurIdx = num2 + start2
  for i in range(len(matchseq2)):
    if matchseq2[i] != '-':
      list2[iCurIdx] = i
      #list2[iCurIdx] = start2 + i
      iCurIdx = iCurIdx + 1

  matchline = ''
  sum_sc, matchnum = 0, 0
  for i in range(len(matchseq1)):
    if matchseq1[i] == '-' or matchseq2[i] == '-':
      matchline = matchline + ' '
      continue
    sc = get_score(matchseq1[i], matchseq2[i])
    sum_sc = sum_sc + sc
    if matchseq1[i] == matchseq2[i]:
        matchline = matchline + '|'
        matchnum = matchnum + 1
    elif sc > 0:    matchline = matchline + '+'
    elif sc == 0:   matchline = matchline + '='
    else:           matchline = matchline + ' '

  # make a two way dictionary seqnum1 -> seqnum2 and the other direction
  for i in range(len(list1)):
    if list1[i] >= 0:
      try:
        idx = list2.index(list1[i])
        dict_list1.append([i, idx])
      except:
        pass

  for i in range(len(list2)):
    if list2[i] >= 0:
      try:
        idx = list1.index(list2[i])
        dict_list2.append([i, idx])
      except:
        pass

  # homology & identity
  sum_self_sc = max_blosum(seq1)
  hmg = float(sum_sc) / float(sum_self_sc) * 100.0
  idt = float(matchnum) / float(len(seq1)) * 100.0

  return {'sequence1': seq1,
          'sequence2': seq2,
          'init_seq1': num1,
          'init_seq2': num2,
          'matchsequence1': matchseq1,
          'matchsequence2': matchseq2,
          'matchline': matchline,
          'init_matchseq1': start1,
          'init_matchseq2': start2,
          'dict12': dict(dict_list1),
          'dict21': dict(dict_list2),
          'sum_blosum62': sum_sc,
          'homology': hmg,
          'identity': idt}

def make_matchnumline(seq_align_dict):
  i1 = seq_align_dict['init_matchseq1'] + seq_align_dict['init_seq1']
  i2 = seq_align_dict['init_matchseq2'] + seq_align_dict['init_seq2']
  seqnum1_list = map(lambda x: ' ',
                      range(len(seq_align_dict['matchsequence1'])+5))
  seqnum2_list = map(lambda x: ' ',
                      range(len(seq_align_dict['matchsequence2'])+5))
  c1, c2 = i1, i2
  for i in range(len(seq_align_dict['matchsequence1'])):
    a = seq_align_dict['matchsequence1'][i]
    if a != '-':
      if c1 % 10 == 1 or c1 == i1:
        s1 = str(c1)
        for j in range(len(s1)):
          seqnum1_list[i+j] = s1[j]
      c1 += 1
  for i in range(len(seq_align_dict['matchsequence2'])):
    a = seq_align_dict['matchsequence2'][i]
    if a != '-':
      if c2 % 10 == 1 or c2 == i2:
        s2 = str(c2)
        for j in range(len(s2)):
          seqnum2_list[i+j] = s2[j]
      c2 += 1

  seqnumline1, seqnumline2 = '', ''
  for a in seqnum1_list:
    seqnumline1 += a
  for a in seqnum2_list:
    seqnumline2 += a
  return seqnumline1, seqnumline2

def transform(pdb_file, seq_align_dict, seq_align_chain, HETATM=False):
  # returns curated PDB file matching sequence numbers
  import os.path
  if not os.path.exists(pdb_file): return ''
  f = open(pdb_file, 'r')
  pdb_lines = f.readlines()
  f.close()
  midx = len(pdb_lines)-1
  for i in range(len(pdb_lines)): # only first model
    if pdb_lines[i].find('ENDMDL') == 0:
      midx = i-1
      break
  pdb_lines = pdb_lines[:midx]
  new_lines = ''
  for line in pdb_lines:
    if len(line) < 50: continue
    if line[0:4] != 'ATOM' and line[0:4] != 'HETA': continue
    if not HETATM and line[0:4] == 'HETA': continue
    if line[0:4] == 'HETA':
      new_lines = new_lines + line
      continue
    ch = line[21:22]
    if ch != ' ' and seq_align_chain != ' ' and seq_align_chain != '-' and \
        ch != seq_align_chain:
      continue
    seqidx2 = int(line[22:26].strip())
    try:
      seqidx = seq_align_dict['dict21'][seqidx2]
    except:
      continue
    line2 = line[0:22] + '%4d' % (seqidx) + line[26:]
    new_lines = new_lines + line2
  return new_lines

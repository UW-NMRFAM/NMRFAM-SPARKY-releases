class Star_Resonance:
    def __init__(self, group = "", atom = "", nuclei = "", shift = 0, atom_index = 0):
        self.group = group 
        self.atom = atom 
        self.nuclei = nuclei 
        self.shift = shift
        self.atom_index = atom_index 
        self.load = True

    def __str__(self):
        load_str = "X" if self.load else ""
        return "%4s %10s %8s %8s %9.2f"%(load_str, self.group, self.atom, self.nuclei, self.shift)

def load_file(input_file):
    resonance_list = []
    infile = open(input_file, 'r')
    columns=[]
    data=[]
    for line in infile:
        linelist=line.split()
        if linelist==[]:
            continue
        if columns==[] and not'_Atom_chem_shift.' in linelist[0]:
            continue
        if 'stop_' in linelist and data!=[]:
            break
        if '_Atom_chem_shift.' in linelist[0]:
            columns.append(linelist[0])
            continue
        if len(linelist)==len(columns) and len(columns)>1:
            data.append(linelist)

    IDindex=columns.index('_Atom_chem_shift.ID') #atom ID e.g 1 
    SeqIDindex=columns.index('_Atom_chem_shift.Seq_ID') #resi num e.g. 1
    Comp_IDindex=columns.index('_Atom_chem_shift.Comp_ID') #resi ID e.g. MET
    Atom_IDindex=columns.index('_Atom_chem_shift.Atom_ID') #atom ID e.ge. CA
    Atom_TypeIndex = columns.index('_Atom_chem_shift.Atom_type') #atom type e.g. C
    Atom_Isotope_numberIndex = columns.index('_Atom_chem_shift.Atom_isotope_number') #isotope number e.g. 15
    Valindex=columns.index('_Atom_chem_shift.Val') #CS value

    for linelist in data:
        new_resonance = Star_Resonance()
        new_resonance.group = convert_residue_symbol(linelist[Comp_IDindex]) + linelist[SeqIDindex]
        new_resonance.atom = linelist[Atom_IDindex]
        new_resonance.nuclei = linelist[Atom_TypeIndex] + linelist[Atom_Isotope_numberIndex]
        new_resonance.shift = float(linelist[Valindex])
        new_resonance.atom_index = int(linelist[IDindex])
        resonance_list.append(new_resonance)

    return resonance_list 

def convert_residue_symbol(residue):

    residue_dict = {
        "ala" : "A",
        "ile" : "I",
        "leu" : "L",
        "val" : "V",
        "phe" : "F",
        "trp" : "W",
        "tyr" : "Y",
        "asn" : "N",
        "cys" : "C",
        "gln" : "Q",
        "met" : "M",
        "ser" : "S",
        "thr" : "T",
        "asp" : "D",
        "glu" : "E",
        "arg" : "R",
        "his" : "H",
        "lys" : "K",
        "gly" : "G",
        "pro" : "P",
    }
    try:
        return residue_dict[residue.lower()]
    except KeyError:
        return residue

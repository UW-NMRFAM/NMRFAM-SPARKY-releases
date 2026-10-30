import pynmrstar
import re

oneTOthree = {'I': 'ILE', 'Q': 'GLN', 'G': 'GLY', 'E': 'GLU', 'C': 'CYS',
            'D': 'ASP', 'S': 'SER', 'K': 'LYS', 'P': 'PRO', 'N': 'ASN',
            'V': 'VAL', 'T': 'THR', 'H': 'HIS', 'W': 'TRP', 'F': 'PHE',
            'A': 'ALA', 'M': 'MET', 'L': 'LEU', 'R': 'ARG', 'Y': 'TYR',
            '?': '.'} # To convert one letter to 3 letter for standard amino acids

class SPARKYtoNMRSTAR(object):

    def __init__(self):
        pass
    def generate_sequence_saveframe(self, seq_name, seq_id, tag_list, data):
        sf = pynmrstar.Saveframe.from_scratch(seq_name, 
                tag_prefix='_Entity')
        sf.add_tag(name='Sf_category', value='entity')
        sf.add_tag(name='Sf_framecode', value=seq_name)
        sf.add_tag(name='ID', value=seq_id)
        tag_map = {
            'Auth_seq_ID': 'seq',
            'Comp_ID': 'res'
        }
        s_loop = pynmrstar.Loop.from_scratch('_Entity_comp_index')
        tags = ['ID','Auth_seq_ID', 'Comp_ID', 'Entry_ID', 'Entity_ID']
        s_loop.add_tag(tags)
        id = 1
        for dat in data:
            d = [id]
            for i in range(1, len(tags)-1):
                if tag_map.has_key(tags[i]):
                    d.append(dat[tag_list.index(tag_map[tags[i]])])
                else:
                    d.append('.')
            d.append(seq_id)
            s_loop.add_data(d)
            id += 1
        sf.add_loop(s_loop)
        return sf

    def generate_distance_saveframe(self, dist_name, dist_id, tag_list, data, 
                                    upper=True):
        dist_name2 = dist_name
        if not upper: dist_name2 = dist_name + '_lower'
        sf = pynmrstar.Saveframe.from_scratch(dist_name2, 
                tag_prefix='_Gen_dist_constraint_list')
        sf.add_tag(name='Sf_category', value='general_distance_constraints')
        sf.add_tag(name='Sf_framecode', value=dist_name2)
        sf.add_tag(name='ID', value=dist_id)
        tag_map = { 
            'Chem_comp_index_ID_1': 'seq', 
            'Chem_comp_ID_1': 'res', 
            'Atom_ID_1': 'atom',
            'Chem_comp_index_ID_2': 'seq2', 
            'Chem_comp_ID_2': 'res2', 
            'Atom_ID_2': 'atom2',
        }
        if upper:
            tag_map['Upper_linear_limit'] = 'value'
        else:
            tag_map['Lower_linear_limit'] = 'value'

        const_loop = pynmrstar.Loop.from_scratch('_Gen_dist_constraint')
        tags = ['ID', 'Chem_comp_index_ID_1', 'Chem_comp_ID_1', 'Atom_ID_1', 
                    'Chem_comp_index_ID_2', 'Chem_comp_ID_2', 'Atom_ID_2',
                    'Upper_linear_limit', 'Lower_linear_limit',
                    'Gen_dist_constraint_list_ID']
        const_loop.add_tag(tags)
        id = 1
        for dat in data:
            d = [id]
            for i in range(1, len(tags)-1):
                if tag_map.has_key(tags[i]):
                    d.append(dat[tag_list.index(tag_map[tags[i]])])
                else:
                    d.append('.')
            d.append(dist_id)
            const_loop.add_data(d)
            id += 1
        sf.add_loop(const_loop)
        return sf

    def generate_angle_saveframe(self, ang_name, ang_id, tag_list, data):
        sf = pynmrstar.Saveframe.from_scratch(ang_name, 
                tag_prefix='_Torsion_angle_constraint_list')
        sf.add_tag(name='Sf_category', value='torsion_angle_constraints')
        sf.add_tag(name='Sf_framecode', value=ang_name)
        sf.add_tag(name='ID', value=ang_id)
        tag_map = { 
            'Auth_seq_ID_': 'seq', 
            'Auth_comp_ID_': 'res',
            'Auth_atom_ID_': 'type',
            'lower': 'Angle_lower_bound_val', 
            'upper': 'Angle_upper_bound_val', 
        }

        const_loop = pynmrstar.Loop.from_scratch('_Torsion_angle_constraint')
        tags = ['ID', 'Torsion_angle_name', 
                'Seq_ID_1', 'Comp_ID_1', 'Atom_ID_1', 
                'Seq_ID_2', 'Comp_ID_2', 'Atom_ID_2', 
                'Seq_ID_3', 'Comp_ID_3', 'Atom_ID_3', 
                'Seq_ID_4', 'Comp_ID_4', 'Atom_ID_4', 
                'Angle_lower_bound_val', 'Angle_upper_bound_val',
                'Auth_seq_ID_1', 'Auth_comp_ID_1', 'Auth_atom_ID_1', 
                'Auth_seq_ID_2', 'Auth_comp_ID_2', 'Auth_atom_ID_2', 
                'Auth_seq_ID_3', 'Auth_comp_ID_3', 'Auth_atom_ID_3', 
                'Auth_seq_ID_4', 'Auth_comp_ID_4', 'Auth_atom_ID_4',
                'Torsion_angle_constraint_list_ID']
        const_loop.add_tag(tags)
        id = 1
        type_idx = tag_list.index('type')
        for dat in data:
            d = [id]
            print dat
            ang_type = dat[type_idx].upper()
            if ang_type == 'PHI':
                atm_list = ['C', 'N', 'CA', 'C']
                seq_list = [ -1,  0,    0,    0]
            else:   
                atm_list = ['N', 'CA', 'C', 'N']
                seq_list = [  0,  0,    0,    1]
            for i in range(1, len(tags)-1):
                tg = tags[i]
                if tg.find('Auth_') != -1:
                    tg2 = tg[:-1]
                else: tg2 = tg
                if not tag_map.has_key(tg2):
                    d.append('.')
                else:
                    if tg.find('Auth_') != -1:
                        idx = int(tg[-1])-1
                        if tg.find('seq') != -1:
                            seq_id = int(dat[tag_list.index('seq')])
                            d.append(str(seq_id + seq_list[idx]))
                        elif tg.find('atom') != -1:
                            d.append(atm_list[idx])
                        else:
                            d.append('.')
                    else:
                        tmp = dat[tag_list.index(tag_map[tags[i]])]
                        d.append(tmp)
                
            d.append(ang_id)
            const_loop.add_data(d)
            id += 1
        sf.add_loop(const_loop)
        return sf

    def generate_rdc_save_frame(self, rdc_name, rdc_id, tag_list, data):
        sf = pynmrstar.Saveframe.from_scratch(rdc_name, 
                tag_prefix='_RDC_constraint_list')
        sf.add_tag(name='Sf_category', value='RDC_constraints')
        sf.add_tag(name='Sf_framecode', value=rdc_name)
        sf.add_tag(name='ID', value=rdc_id)

        tag_map = {
            'Auth_seq_ID_1': 'seq',
            'Auth_comp_ID_1': 'res',
            'Auth_atom_ID_1': 'atom',
            'Auth_seq_ID_2': 'seq2',
            'Auth_comp_ID_2': 'res2',
            'Auth_atom_ID_2': 'atom2',
            'RDC_val': 'rdc',
            'RDC_val_err': 'err',
            'Entry_ID': 'ori'
        }
        rdc_loop = pynmrstar.Loop.from_scratch('_RDC_constraint')
        tags = ['ID', 'Assembly_atom_ID_1', 'Entity_assembly_ID_1', 
            'Entity_ID_1', 'Comp_index_ID_1', 'Seq_ID_1', 'Comp_ID_1', 
            'Atom_ID_1', 'Resonance_ID_1', 'Assembly_atom_ID_2', 
            'Entity_assembly_ID_2', 'Entity_ID_2', 'Comp_index_ID_2', 
            'Seq_ID_2', 'Comp_ID_2', 'Atom_ID_2', 'Resonance_ID_2', 
            'RDC_val', 'RDC_lower_bound', 'RDC_upper_bound', 'RDC_val_err', 
            'Source_experiment_ID', 'Auth_asym_ID_1', 'Auth_seq_ID_1', 
            'Auth_comp_ID_1', 'Auth_atom_ID_1', 'Auth_asym_ID_2', 
            'Auth_seq_ID_2', 'Auth_comp_ID_2', 'Auth_atom_ID_2', 'Entry_ID', 
            'RDC_constraint_list_ID']
        rdc_loop.add_tag(tags)
        id = 1
        for dat in data:
            d = [id]
            for i in range(1, len(tags)-1):
                if tag_map.has_key(tags[i]):
                    d.append(dat[tag_list.index(tag_map[tags[i]])])
                else:
                    d.append('.')
            d.append(seq_id)
            rdc_loop.add_data(d)
            id += 1
        sf.add_loop(rdc_loop)
        return sf

    def generate_saxs_saveframe(self, saxs_name, saxs_id, tag_list, data):
        sf = pynmrstar.Saveframe.from_scratch(saxs_name, 
                tag_prefix='_SAXS_constraint_list')
        sf.add_tag(name='Sf_category', value='SAXS_constraints')
        sf.add_tag(name='Sf_framecode', value=saxs_name)
        sf.add_tag(name='ID', value=saxs_id)
        tag_map = {
            'Q_value': 'q',
            'Intensity_val': 'Iq',
            'Intensity_val_err': 'err'
        }
        saxs_loop = pynmrstar.Loop.from_scratch('_SAXS_constraint')
        tags = ['ID','Q_value', 'Intensity_val', 'Intensity_val_err', 
                'Entry_ID', 'Sf_ID', 'SAXS_constraint_list_ID']
        saxs_loop.add_tag(tags)
        id = 1
        for dat in data:
            d = [id]
            for i in range(1, len(tags)-1):
                if tag_map.has_key(tags[i]):
                    d.append(dat[tag_list.index(tag_map[tags[i]])])
                else:
                    d.append('.')
            d.append(saxs_id)
            saxs_loop.add_data(d)
            id += 1
        sf.add_loop(saxs_loop)
        return sf

    def generate_assigned_cs_list_saveframe(self, pl_name, pl_id, tag_list, data):
        '''
        Generates Assigned chemical shift save frame
        :param pl_name: Peak list name
        :param pl_id: int Peak list ID
        :param tag_list: list of tags in order
        :param data: data set
        :return: safe frame
        '''
        sf = pynmrstar.Saveframe.from_scratch(pl_name, 
                tag_prefix='Assigned_chem_shift')
        sf.add_tag(name='Sf_category', value='assigned_chemical_shifts')
        sf.add_tag(name='Sf_framecode', value=pl_name)
        sf.add_tag(name='ID', value=pl_id)
        tag_map = {
            'chain': 'Entity_assembly_ID',
            'res': 'Comp_ID',
            'atom': 'Atom_ID',
            'seq': 'Comp_index_ID',
            'atom_type': 'Atom_type',
            'atom_iso': 'Atom_isotope_number',
            'cs': 'Val',
            'cs_err':'Val_err',
            'amb_code': 'Ambiguity_code'
        }
        cs_loop = pynmrstar.Loop.from_scratch('Atom_chem_shift')
        tags = ['ID']
        for t in tag_list:
            try:
                tags.append(tag_map[t])
            except KeyError:
                print ('Tag not in the expected list of tags:{}',t)
        if 'chain' not in tag_list:
            tags.append(tag_map['chain'])
        if 'amb_code' not in tag_list:
            tags.append(tag_map['amb_code'])
        tags.append('Assigned_chem_shift_list_ID')
        cs_loop.add_tag(tags)
        id = 1
        for dat in data:
            d = [id]
            for i in range(len(tag_list)):
                if tag_list[i] == 'res':
                    r = dat[i]
                    if len(r) == 1:
                        r = oneTOthree[r]
                    d.append(r)
                else:
                    if dat[i] == '':
                        d.append('.')
                    else:
                        d.append(dat[i])
            if 'chain' not in tag_list:
                d.append('.')
            if 'amb_code' not in tag_list:
                d.append('.')
            d.append(pl_id)
            cs_loop.add_data(d)
            id += 1
        sf.add_loop(cs_loop)
        return sf


    def generate_peak_list_saveframe(self, experiment_name,
                                     dimensions,
                                     atom_type,  # list atom type in each dimension
                                     isotope,  # isotope value for each atom type
                                     region,  # list region in each dimension like CA,CB,N
                                     pl_id,
                                     tag_list,  # actual peak list tags
                                                # w1,w2,w3,w4,.. cs in each dim
                                                # v (volume),h(height),p(probability),
                                                # lw1,lw2,lw3, line widht
                                                # la1,la2,la , assigned lables like E1CA, I3CD1, etss
                                                # r1,r2,.. assigned residue name each dim
                                                # s1, s2, s3.. assigned seq id in each dim
                                                # a1, a2,... assigned atom name in each dime
                                     data,  # same number of values as tag_list,
                                     peak_list_name=None,
                                     experiment_class=None,  # example H-H(C).through-space
                                     experiment_type=None,  # example 13C-NOESY-HSWC
                                     freq=None,  # list freq in each dimension
                                     sw=None,  # sweep width in each dimension
                                     sw_unit=None  # sweep width unit
                                     ):
        '''
        Generates peak list save frame
        :param experiment_name: Name of the experiment
        :param dimensions: Number of dimensions
        :param atom_type: List of atom type in each dimension
        :param isotope: List of isotope value for atom in each dimension
        :param region: List of region for each dimension like CA, CB, etc..
        :param pl_id: int peak list id
        :param tag_list: List of tags in order
        :param data: data
        :param peak_list_name: Name of the peak list
        :param experiment_class: Experiment class
        :param experiment_type: Experiment type
        :param freq: list of spectrometer frequency in each dimension
        :param sw: sweep width in each dimension
        :param sw_unit: unit for sweep with in each dimension
        :return: save frame
        '''
        tag_map = {
            'w1': 'Position_1',
            'w2': 'Position_2',
            'w3': 'Position_3',
            'w4': 'Position_4',
            'v': 'Volume',
            'h': 'Height',
            'p': 'Figure_of_merit',
            'lw1': 'Line_width_1',
            'lw2': 'Line_width_2',
            'lw3': 'Line_width_3',
            'lw4': 'Line_width_4',
            'r1': 'Comp_ID_1',
            'r2': 'Comp_ID_2',
            'r3': 'Comp_ID_3',
            'r4': 'Comp_ID_4',
            's1': 'Comp_index_ID_1',
            's2': 'Comp_index_ID_2',
            's3': 'Comp_index_ID_3',
            's4': 'Comp_index_ID_4',
            'a1': 'Atom_ID_1',
            'a2': 'Atom_ID_2',
            'a3': 'Atom_ID_3',
            'a4': 'Atom_ID_4',
        }
        if peak_list_name is None:
            peak_list_name = 'peak_list_{}_{}'.format(pl_id, experiment_name)
        sf = pynmrstar.Saveframe.from_scratch(peak_list_name, tag_prefix='Spectral_peak_list')
        sf.add_tag(name='Sf_category', value='spectral_peak_list')
        sf.add_tag(name='Sf_framecode', value=peak_list_name)
        sf.add_tag(name='Experiment_name', value=experiment_name)
        if experiment_class is not None:
            sf.add_tag('Experiment_class', value=experiment_class)
        if experiment_type is not None:
            sf.add_tag(name='Experiment_type', value=experiment_type)
        sf.add_tag(name='Number_of_spectral_dimensions', value=dimensions)
        spect_dim_loop = pynmrstar.Loop.from_scratch('Spectral_dim')
        tags = ['ID']
        if freq is not None:
            tags.append('Spectrometer_frequency')
        tags.append('Atom_type')
        tags.append('Atom_isotope_number')
        tags.append('Spectral_region')
        if sw is not None:
            tags.append('Sweep_width')
        if sw_unit is not None:
            tags.append('Sweep_with_units')
        tags.append('Spectral_peak_list_ID')
        spect_dim_loop.add_tag(tags)
        for i in range(dimensions):
            d = []
            d.append(i + 1)
            if freq is not None:
                d.append(freq[i])
            d.append(atom_type[i])
            d.append(isotope[i])
            d.append(region[i])
            if sw is not None:
                d.append(sw[i])
            if sw_unit is not None:
                d.append(sw_unit[i])
            d.append(pl_id)
            print
            spect_dim_loop.add_data(d)
        sf.add_loop(spect_dim_loop)
        peak_row_loop = pynmrstar.Loop.from_scratch('Peak_row_format')
        tags = ['ID']
        for t in tag_list:
            if t== 'la1':
                tags.append(tag_map['r1'])
                tags.append(tag_map['s1'])
                tags.append(tag_map['a1'])
            elif t== 'la2':
                tags.append(tag_map['r2'])
                tags.append(tag_map['s2'])
                tags.append(tag_map['a2'])
            elif t== 'la3':
                tags.append(tag_map['r3'])
                tags.append(tag_map['s3'])
                tags.append(tag_map['a3'])
            elif t== 'la4':
                tags.append(tag_map['r4'])
                tags.append(tag_map['s4'])
                tags.append(tag_map['a4'])
            else:
                try:
                    tags.append(tag_map[t])
                except KeyError:
                    print ('Tag not in the expected list of tags:{}', t)
        tags.append('Peak_list_ID')
        peak_row_loop.add_tag(tags)
        id = 1
        for dat in data:
            d = [id]
            for i in range(len(tag_list)):
                if tag_list[i] in ['la1','la2','la3','la4'] :
                    lb = re.findall(r'(\S)(\d)(\S+)', dat[i])
                    r = lb[0][0]
                    s = lb[0][1]
                    a = lb[0][1]
                    if len(r)==1:
                        r = oneTOthree[r]
                    d.append(r)
                    d.append(s)
                    d.append(a)
                if tag_list[i] in ['r1', 'r2', 'r3','r4']:
                    r = dat[i]
                    if len(r)==1:
                        r = oneTOthree[r]
                    d.append(r)
                else:
                    if dat[i]=='':
                        d.append('.')
                    else:
                        d.append(dat[i])
            d.append(pl_id)
            peak_row_loop.add_data(d)
            id+=1
        sf.add_loop(peak_row_loop)
        pk_char_lp = pynmrstar.Loop.from_scratch('Peak_char')
        pk_row_tags = peak_row_loop.get_tag_names()
        tags = ['Peak_ID','Spectral_dim_ID','Chemical_shift_val','Spectral_peak_list_ID']
        pk_char_lp.add_tag(tags)
        for dat in peak_row_loop.data:
            pk_char_lp.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                 1,dat[pk_row_tags.index('_Peak_row_format.Position_1')],pl_id])
            pk_char_lp.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                 2, dat[pk_row_tags.index('_Peak_row_format.Position_2')], pl_id])
            if dimensions == 3:
                pk_char_lp.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                     3, dat[pk_row_tags.index('_Peak_row_format.Position_3')], pl_id])
            if dimensions == 4:
                pk_char_lp.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                     4, dat[pk_row_tags.index('_Peak_row_format.Position_4')], pl_id])
                pk_char_lp.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                     4, dat[pk_row_tags.index('_Peak_row_format.Position_4')], pl_id])
        sf.add_loop(pk_char_lp)

        apk_loop = pynmrstar.Loop.from_scratch('Assigned_peak_chem_shift')
        tags = ['Peak_ID','Spectral_dim_ID','Val','Figure_of_merit','Comp_index_ID','Comp_ID','Atom_ID',
                'Spectral_peak_list_ID']
        apk_loop.add_tag(tags)
        for dat in peak_row_loop.data:
            if '_Peak_row_format.Figure_of_merit' in pk_row_tags:
                apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],1,
                                   dat[pk_row_tags.index('_Peak_row_format.Position_1')],
                                   dat[pk_row_tags.index('_Peak_row_format.Figure_of_merit')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_1')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_ID_1')],
                                   dat[pk_row_tags.index('_Peak_row_format.Atom_ID_1')],pl_id])
                apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 2,
                                   dat[pk_row_tags.index('_Peak_row_format.Position_2')],
                                   dat[pk_row_tags.index('_Peak_row_format.Figure_of_merit')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_2')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_ID_2')],
                                   dat[pk_row_tags.index('_Peak_row_format.Atom_ID_2')], pl_id])
                if dimensions == 3:
                    apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 3,
                                       dat[pk_row_tags.index('_Peak_row_format.Position_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Figure_of_merit')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Atom_ID_3')], pl_id])
                if dimensions == 4:
                    apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 3,
                                       dat[pk_row_tags.index('_Peak_row_format.Position_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Figure_of_merit')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.ID_3')], pl_id])
                    apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 4,
                                       dat[pk_row_tags.index('_Peak_row_format.Position_4')],
                                       dat[pk_row_tags.index('_Peak_row_format.Figure_of_merit')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_4')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_ID_4')],
                                       dat[pk_row_tags.index('_Peak_row_format.Atom_ID_4')], pl_id])
            else:
                apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 1,
                                   dat[pk_row_tags.index('_Peak_row_format.Position_1')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_1')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_ID_1')],
                                   dat[pk_row_tags.index('_Peak_row_format.Atom_ID_1')], pl_id])
                apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 2,
                                   dat[pk_row_tags.index('_Peak_row_format.Position_2')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_2')],
                                   dat[pk_row_tags.index('_Peak_row_format.Comp_ID_2')],
                                   dat[pk_row_tags.index('_Peak_row_format.Atom_ID_2')], pl_id])
                if dimensions == 3:
                    apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 3,
                                       dat[pk_row_tags.index('_Peak_row_format.Position_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Atom_ID_3')], pl_id])
                if dimensions == 4:
                    apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 3,
                                       dat[pk_row_tags.index('_Peak_row_format.Position_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_ID_3')],
                                       dat[pk_row_tags.index('_Peak_row_format.ID_3')], pl_id])
                    apk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')], 4,
                                       dat[pk_row_tags.index('_Peak_row_format.Position_4')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_index_ID_4')],
                                       dat[pk_row_tags.index('_Peak_row_format.Comp_ID_4')],
                                       dat[pk_row_tags.index('_Peak_row_format.Atom_ID_4')], pl_id])

        sf.add_loop(apk_loop)
        if '_Peak_row_format.Volume' in pk_row_tags or '_Peak_row_format.Height' in pk_row_tags:
            pk_gen_char_loop = pynmrstar.Loop.from_scratch('Peak_general_char')
            tags = ['Peak_ID','Intensity_val','Measurement_method','Spectral_peak_list_ID']
            pk_gen_char_loop.add_tag(tags)
            for dat in peak_row_loop.data:
                if '_Peak_row_format.Volume' in pk_row_tags:
                    pk_gen_char_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                               dat[pk_row_tags.index('_Peak_row_format.Volume')],
                                               'volume',pl_id])
                if '_Peak_row_format.Height' in pk_row_tags:
                    pk_gen_char_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                               dat[pk_row_tags.index('_Peak_row_format.Height')],
                                               'height',pl_id])
            sf.add_loop(pk_gen_char_loop)
        if '_Peak_row_format.Figure_of_merit' in pk_row_tags:
            pk_loop = pynmrstar.Loop.from_scratch('Peak')
            tags = ['ID','Figure_of_merit','Spectral_peak_list_ID']
            pk_loop.add_tag(tags)
            for dat in peak_row_loop.data:
                pk_loop.add_data([dat[pk_row_tags.index('_Peak_row_format.ID')],
                                  dat[pk_row_tags.index('_Peak_row_format.Figure_of_merit')],
                                  pl_id])
            sf.add_loop(pk_loop)
        return sf


    @staticmethod
    def read_pine_sparky_2D_peak_list(fname=None, content=None, p=True, h=False):
        '''
        Reads pine sparky 2d peak list
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'\s*([A-Za-z?])(\d*)(\S*)-([A-Za-z?])(\d*)(\S*)\s+(\S+)\s+(\S+)\s+(\S*)\n', data)
        if p:
            tag_list = ['r1','s1','a1','r2','s2','a2','w1','w2','p']
        else:
            tag_list = ['r1','s1','a1','r2','s2','a2','w1','w2']
            if h:
                tag_list.append('h')
        return tag_list, d

    @staticmethod
    def read_pine_sparky_3D_peak_list(fname=None, content=None, p=True, h=False):
        '''
        Reads pine sparky 3d peak list
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'\s*([A-Za-z])(\d+)(\S+)-([A-Za-z])(\d+)(\S+)-([A-Za-z])(\d+)(\S+)\s+'
                       r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\n', data)
        if p:
            tag_list = ['r1','s1','a1','r2','s2','a2','r3','s3','a3','w1','w2','w3','p']
        else:
            tag_list = ['r1','s1','a1','r2','s2','a2','r3','s3','a3','w1','w2','w3']
            if h:
                tag_list.append('h')
        return tag_list, d

    @staticmethod
    def read_pine_sparky_4D_peak_list(fname=None, content=None, p=True, h=False):
        '''
        Reads pine sparky 4d peak list
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'\s*([A-Za-z])(\d+)(\S+)-([A-Za-z])(\d+)(\S+)-([A-Za-z])(\d+)(\S+)-([A-Za-z])(\d+)(\S+)\s+'
                       r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\n', data)
        if p:
            tag_list = ['r1','s1','a1','r2','s2','a2','r3','s3','a3','r4','s4','a4','w1','w2','w3','w4','p']
        else:
            tag_list = ['r1','s1','a1','r2','s2','a2','r3','s3','a3','r4','s4','a4','w1','w2','w3','w4']
            if h:
                tag_list.append('h')
        return tag_list, d

    @staticmethod
    def read_sparky_resonance_list(fname=None, content=None):
        '''
        Reads pine sparky resonance list
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        #d = re.findall(r'\s*([A-Za-z])(\d+)\s+(\S+)\s+(\d+)(\S)\s+(\S+)\s+(\S+)\s+(\S+)\s',data) # Last col disabled
        d = re.findall(r'\s*([A-Za-z])(\d+)\s+(\S+)\s+(\d+)(\S)\s+(\S+)\s+(\S+)\s+\S+\s', data)
        tag_list = ['res','seq','atom','atom_iso','atom_type','cs','cs_err']
        return tag_list, d

    @staticmethod
    def read_oneletter_sequence(fname=None, content=None):
        '''
        Reads one-letter sequence file e.g. AGLR....\n
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        a = re.findall(r'([A-Za-z]+)', data)
        c = ''
        for b in a:
            c += b
        c = list(c)
        d = []
        for i in range(len(c)):
            d.append((i+1, oneTOthree[c[i]]))
        tag_list = ['seq','res']
        return tag_list, d

    @staticmethod
    def read_dyana_sequence(fname=None, content=None):
        '''
        Reads dyana sequence file e.g. ALA 1\n
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'([A-Za-z]+)\s*([0-9]+)', data)
        tag_list = ['res', 'seq']
        return tag_list, d

    @staticmethod
    def read_dyana_distance(fname=None, content=None):
        '''
        Reads dyana distance file e.g. 1 ALA HA 4 GLY HA 5.00
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'([0-9]+)\s*([A-Za-z]+)\s*([A-Za-z0-9]+)\s*([0-9]+)\s*([A-Za-z]+)\s*([A-Za-z0-9]+)\s*([.0-9]+)', data)
        tag_list = ['seq','res','atom','seq2','res2','atom2','value']
        return tag_list, d

    @staticmethod
    def read_dyana_angle(fname=None, content=None):
        '''
        Reads dyana angle file e.g.  6 PHE  PHI -132.394  -84.586
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'([0-9]+)\s*([A-Za-z]+)\s*([A-Za-z]+)\s*([-+]?[.0-9]+)\s*([-+]?[.0-9]+)', data)
        tag_list = ['seq','res','type','lower','upper']
        return tag_list, d

    @staticmethod
    def read_rdc(fname=None, content=None):    
        '''
        Reads rdc file e.g.
#Orientation  Magnitude  Rhombicity  ORI residue number
       1        999      999           1
# First atom Second atom  RDC Error Weight Orientation
  6 ARG    H      6 ARG    N       3.16 1.000   1.000   1
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'([0-9]+)\s*([A-Za-z]+)\s*([A-Za-z]+)\s*([0-9]+)\s*([A-Za-z]+)\s*([A-Za-z]+)\s*([-+]?[.0-9]+)\s*([.0-9]+)\s*([.0-9]+)', data)        
        tag_list = ['seq','res','atom','seq2','res2','atom2','rdc','err','weight','ori']
        return tag_list, d

    @staticmethod
    def read_saxs(fname=None, content=None):    
        '''
        Reads saxs file e.g.
 9.327160e-003  2.718903e+002  2.787016e+000
 9.625790e-003  2.751569e+002  2.695218e+000
 9.924410e-003  2.738677e+002  2.490705e+000
        :param fname: file name
        :return: list of tags, data
        '''
        if fname != None:
            with open(fname, 'r') as fin:
                data = fin.read()
        else:
            data = content
        d = re.findall(r'([.0-9]+[eE][+/-][0-9]+)\s*([.0-9]+[eE][+/-][0-9]+)\s*([.0-9]+[eE][+/-][0-9]+)', data)
        tag_list = ['q','Iq','err']
        return tag_list, d

    @staticmethod
    def write_save_frame(sf, file_name):
        '''
        Writes single save frame in a file
        :param sf: save frame
        :param file_name: output file name
        :return:
        '''
        with open(file_name,'w') as wstarsf:
            wstarsf.write(str(sf))


    @staticmethod
    def write_star_file(sf_list, data_set_name, file_name=None):
        '''
        Writes list of save frames as a NMR-STAR file
        :param sf_list: list of save frames
        :param data_set_name: Nme of data set
        :param file_name: file name
        :return:
        '''
        if file_name is None:
            file_name = '{}.str'.format(data_set_name)
        ent = pynmrstar.Entry.from_scratch(data_set_name)
        for sf in sf_list:
            ent.add_saveframe(sf)
        ent.normalize
        with open(file_name,'w') as wstarfile:
            wstarfile.write(str(ent))

if __name__ == "__main__":
    # How to use this library
    sc = SPARKYtoNMRSTAR()
    # Reading data from pine sparky outputs
    tl1, pl1 = sc.read_pine_sparky_2D_peak_list('sparky_dataset/sparky_N15-HSQC.list')
    print (tl1)
    print (pl1[0])
    # Generating saveframe
    sf1 = sc.generate_peak_list_saveframe(experiment_name='N15-HSQC',dimensions=2,atom_type = ['N','H'],
                                          isotope=[15,1],region=['NH','HN'],pl_id=1,tag_list=tl1,data=pl1)
    tl2, pl2 = sc.read_pine_sparky_3D_peak_list(
                fname='sparky_dataset/sparky_CBCACONH.list')
    # 3d example
    sf2 = sc.generate_peak_list_saveframe(experiment_name='3D-CBCA(CO)NH',dimensions=3,atom_type=['N','C','H'],
                                          isotope=[15,13,1],region=['NH','CA,CB','HN'],pl_id=2,tag_list=tl2,
                                          data=pl2,experiment_class='CBCA(CO) N though bond')
    # cs list example
    tl3, pl3 = sc.read_sparky_resonance_list(
                fname='sparky_dataset/sparkyresonances.list')
    sf3 = sc.generate_assigned_cs_list_saveframe(pl_name='test_cs_list',pl_id=1,tag_list=tl3,data=pl3)

    # writing single save frame
    sc.write_save_frame(sf1,'sparky_dataset/n15hsqc_peaks.str')
    sc.write_save_frame(sf2, 'sparky_dataset/cbcaconh_peaks.str')
    sc.write_save_frame(sf1, 'sparky_dataset/assigned_cs.str')

    #writing single file file name optional it will write datasetname.str as output file
    sc.write_star_file([sf1,sf2,sf3],data_set_name='test_data_set_ubiquitin',
                       file_name='sparky_dataset/test_out.str')





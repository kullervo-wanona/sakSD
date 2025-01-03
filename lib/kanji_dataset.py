
import numpy as np
import os
import re
import pickle
import shutil

import cairosvg
import io
from PIL import Image

def rec_get_all_strokes_from_svg_el(svg_el):
    if svg_el.tag == 'path': 
        svg_el.attrib['d']
        return [svg_el.attrib['d']]

    strokes = []
    for ent in list(svg_el): 
        strokes += rec_get_all_strokes_from_svg_el(ent)
    return strokes

def cubic_bezier_extract(d_curve_str):

    m_all_pos = [x.start() for x in re.finditer('m', d_curve_str)]
    M_all_pos = [x.start() for x in re.finditer('M', d_curve_str)]
    assert (d_curve_str[0] in ['m', 'M'] and (len(m_all_pos) + len(M_all_pos)) == 1)
    c_all_pos = [x.start() for x in re.finditer('c', d_curve_str)]
    s_all_pos = [x.start() for x in re.finditer('s', d_curve_str)]
    C_all_pos = [x.start() for x in re.finditer('C', d_curve_str)]
    S_all_pos = [x.start() for x in re.finditer('S', d_curve_str)]
    m_c_s_all_pos = [0] + sorted(c_all_pos + s_all_pos + C_all_pos + S_all_pos) + [len(d_curve_str)]

    splits = []
    for i in range(len(m_c_s_all_pos)-1):
        splits.append(d_curve_str[m_c_s_all_pos[i]:m_c_s_all_pos[i+1]])

    param_list = []
    for part in splits: 
        part_type = part[0]
        # params_1 = part[1:].split(',')
        params_raw = list(filter(None, re.split(r'(\s|\,)', part[1:].strip())))
        params = []
        for p in params_raw: 
            if len(p.strip()) > 0 and not (len(p.strip()) == 1 and p.strip()[0] == ','):
                params.append(p.strip())

        params_ext = []
        for param in params: 
            neg_all_pos = [x.start() for x in re.finditer('-', param)]

            if len(neg_all_pos) == 0: params_ext.append(param)
            else:
                split_pos = neg_all_pos + [len(param)] if neg_all_pos[0] == 0 else [0] + neg_all_pos + [len(param)]
                in_splits = []
                for j in range(len(split_pos)-1):
                    in_splits.append(param[split_pos[j]:split_pos[j+1]])
                params_ext = params_ext + in_splits
        
        params_floated = [float(e.strip()) for e in params_ext]

        if part_type in ['m', 'M']: 
            assert (len(params_floated) == 2)
            param_list.append({'type': part_type, 'params': params_floated})
        elif part_type in ['c', 'C']: 
            assert (len(params_floated) % 6 == 0)
            for k in range(int(len(params_floated)/6)):
                param_list.append({'type': part_type, 'params': params_floated[k*6:(k+1)*6]})
        elif part_type in ['s', 'S']: 
            assert (len(params_floated) % 4 == 0)
            for k in range(int(len(params_floated)/4)):
                param_list.append({'type': part_type, 'params': params_floated[k*4:(k+1)*4]})

    return param_list

def svg_str_from_cubic_bezier_params(cb_params_list, height, width, stroke_width_px):
    svg_str = '<svg xmlns="http://www.w3.org/2000/svg" height="' + str(int(height)) + '" width="' + str(int(width)) + '">'
    # svg_str += '<g transform="translate(0, 0)">'

    for cb_params in cb_params_list:
        svg_str += '<path d='
        svg_str += '"' 

        m_param = cb_params[0]
        assert (m_param['type'] in ['m', 'M'])
        svg_str += m_param['type'] + ' ' + str(m_param['params'][0]) + ',' + str(m_param['params'][1])
        for curve_param in cb_params[1:]:
            assert (curve_param['type'] in ['c', 's', 'C', 'S'])
            curve_str = curve_param['type'] + ' ' 

            for i, param_f in enumerate(curve_param['params']):
                if i % 2 == 0: curve_str += ' ' + str(param_f)
                else: curve_str += ',' + str(param_f) 
            svg_str += ' ' + curve_str

        svg_str += '"'
        svg_str += ' style="fill:none;stroke:#000;stroke-width:' + str(int(stroke_width_px)) + 'px;"'
        svg_str += '/>'

    # svg_str +='</g>'
    svg_str +='</svg>'
    return svg_str

def add_white_background_trans_image(init_np):
    transp = init_np[:, :, -1, np.newaxis]
    np_image = init_np[:, :, :3] + (255-transp)
    return np_image

def svg_str_to_np_image(svg_str):
    svg_str_byte = svg_str.encode('utf-8')
    mem = io.BytesIO()
    cairosvg.svg2png(bytestring=svg_str_byte, write_to=mem)
    return np.array(Image.open(mem)) 

def save_np_image(np_image, path):
    im = Image.fromarray(np_image)
    im.save(path)

def get_kanji_metadata_dict(kanji_char_entries):
    metadata_dict = {}
    for i, char_entry in enumerate(kanji_char_entries):
        assert ((char_entry).tag == 'character')
        char_el_list = list(char_entry)
        
        info_dict = {}
        ucs_hex = None
        for e in char_el_list: 
            if e.tag == 'codepoint':
                code_point_els = list(e)
                for code_point_el in code_point_els:
                    if code_point_el.attrib['cp_type'] == 'ucs':
                        assert (ucs_hex is None)
                        ucs_hex = code_point_el.text
                        for _ in range(5-len(ucs_hex)):
                            ucs_hex = '0' + ucs_hex

                assert (ucs_hex is not None)

            elif e.tag == 'reading_meaning':
                for el in list(e):
                    if el.tag == 'rmgroup':
                        if 'meanings' not in info_dict: info_dict['meanings'] = []

                        for rm_el in list(el):
                            if rm_el.tag == 'meaning':
                                if len(rm_el.attrib) == 0:
                                    info_dict['meanings'].append(rm_el.text)
                                # else:
                                #     print(rm_el.attrib)

        assert (ucs_hex is not None)
        metadata_dict[ucs_hex.lower()] = info_dict

    meaning_filtered_metadata_dict = {}
    for key in metadata_dict: 
        if 'meanings' in metadata_dict[key] and len(metadata_dict[key]['meanings']) > 0:
            meaning_filtered_metadata_dict[key] = metadata_dict[key]

    return metadata_dict, meaning_filtered_metadata_dict

def filter_meaning_and_svg_hexes(meaning_filtered_metadata_dict, svg_entries):
    meaning_and_svg_set = set()
    for k, svg_entry in enumerate(svg_entries): 
        kanji_id_str = svg_entry.attrib['id']
        kanji_id_hex = kanji_id_str[len('kvg:kanji_'):].lower()
        assert(len(kanji_id_hex) == 5)
        assert (svg_entry.tag == 'kanji')
        assert (kanji_id_str[:len('kvg:kanji_')])
        if kanji_id_hex in meaning_filtered_metadata_dict:
            meaning_and_svg_set.add(kanji_id_hex)
    return meaning_and_svg_set

def create_dataset(svg_all_entries, meaning_and_svg_set, im_height, im_width, im_stroke_width_px, 
                   dataset_dir, kanji_metadata_dict=None, create_svgs=True):
    if os.path.exists(dataset_dir): shutil.rmtree(dataset_dir)
    if not os.path.exists(dataset_dir): os.makedirs(dataset_dir)
    if create_svgs and not os.path.exists(dataset_dir + 'svg/'): os.makedirs(dataset_dir + 'svg/')

    images_np = np.zeros((len(meaning_and_svg_set), im_height, im_width, 3), np.uint8)
    labels = []

    count = 0 
    for k, svg_entry in enumerate(svg_all_entries): 

        kanji_id_str = svg_entry.attrib['id']
        kanji_id_hex = kanji_id_str[len('kvg:kanji_'):].lower()

        assert(len(kanji_id_hex) == 5)
        assert (svg_entry.tag == 'kanji')
        assert (kanji_id_str[:len('kvg:kanji_')])

        if kanji_id_hex not in meaning_and_svg_set: continue

        strokes = []
        for e in list(svg_entry):
            strokes += rec_get_all_strokes_from_svg_el(e)

        cubic_bezier_params_list = [cubic_bezier_extract(e) for e in strokes]
        svg_str = svg_str_from_cubic_bezier_params(cubic_bezier_params_list, 
            height=im_height, width=im_width, stroke_width_px=im_stroke_width_px)
        svg_np = add_white_background_trans_image(svg_str_to_np_image(svg_str))
        if create_svgs: save_np_image(svg_np, dataset_dir + 'svg/' + "%04d" % (count) + '__' + kanji_id_hex +'.png')

        images_np[count, :, :, :] = svg_np

        if kanji_metadata_dict is not None:
            in_metadata_dict = kanji_id_hex in kanji_metadata_dict
            has_meaning_entry = 'meanings' in kanji_metadata_dict[kanji_id_hex] if kanji_id_hex in kanji_metadata_dict else False
            n_meaning_entries = len(kanji_metadata_dict[kanji_id_hex]['meanings']) \
                if kanji_id_hex in kanji_metadata_dict and 'meanings' in kanji_metadata_dict[kanji_id_hex] else 0

            print('\n\n############################################################################################\n')
            print('hex: ', kanji_id_hex, ' in_metadata_dict: ', in_metadata_dict, ' has_meaning_entry: ', 
                  has_meaning_entry, ' n_meaning_entries: ', n_meaning_entries)
            if n_meaning_entries > 0: 
                print('\n##############################################\n')
                for meaning in kanji_metadata_dict[kanji_id_hex]['meanings']: print(meaning + '\n')
            print('\n\n############################################################################################\n')
        
        labels.append(kanji_metadata_dict[kanji_id_hex]['meanings'])
        count += 1

    with open(dataset_dir + 'images.npy', 'wb') as f: np.save(f, images_np)
    with open(dataset_dir + 'labels.pickle', 'wb') as f: pickle.dump(labels, f, protocol=pickle.HIGHEST_PROTOCOL)













# DATASET_DIR = './dataset/'

# # STROKE_WIDTH = 3
# # IM_HEIGHT = 109
# # IM_WIDTH = 109
# # kanji_char_entries = list(ET.parse('kanjidic2.xml').getroot())[1:]
# # svg_all_entries = list(ET.parse('kanjivg-20220427.xml').getroot())
# # kanji_metadata_dict, meaning_filtered_metadata_dict = get_kanji_metadata_dict(kanji_char_entries)
# # meaning_and_svg_set = filter_meaning_and_svg_hexes(meaning_filtered_metadata_dict, svg_all_entries)
# # create_dataset(svg_all_entries, meaning_and_svg_set, IM_HEIGHT, IM_WIDTH, STROKE_WIDTH, DATASET_DIR, kanji_metadata_dict, create_svgs=True)

# with open(DATASET_DIR + 'images.npy', 'rb') as f: loaded_images_np = np.load(f)
# with open(DATASET_DIR + 'labels.pickle', 'rb') as f: loaded_labels = pickle.load(f)

# kanji_tree = ET.parse('kanjidic2.xml')
# svg_tree = ET.parse('kanjivg-20220427.xml')
# kanji_tree_root = kanji_tree.getroot()
# svg_tree_root = svg_tree.getroot()
# kanji_all_entries = list(kanji_tree_root)
# kanji_header_entry = kanji_all_entries[0]
# assert ((kanji_header_entry).tag == 'header')

# d_curve_examples = [
#         'M51.63,9.5c0.1,0.76,0.47,2.03-0.19,3.05c-4.59,7.11-14.6,20.33-34.18,29.2',
#         'M53.25,12.5c4.88,4.89,25.88,20.84,31.26,24.42c1.83,1.21,4.17,1.73,5.99,2.08',
#         ####################
#         'M41.79,31.28c0.49,0.1,2.77,0.65,3.26,0.6C49,31.5,55.75,30.25,63.7,29.7c0.81-0.06,2,0.05,2.41,0.1',
#         ####################
#         'M33,40.01c0.45,0.31,0.98,1.04,1.1,1.44c1.49,5.23,2.14,7.97,3.15,12.33',
#         'M34.25,41.39c12.43-1.58,29.06-3.34,36.18-3.73c2.6-0.15,3.66,1.36,3.29,2.22c-1.54,3.55-1.97,5.38-2.97,9.13',
#         'M37.85,51.72c9.92-0.5,22.59-2.08,35.25-2.57',
#         ####################
#         'M19.48,61.84c2.31,0.87,2.77,1.24,6.11,0.58C32.75,61,41.5,58.78,43.6,58.65c2.38-0.14,3.77,1.15,3.84,3.49c0.08,2.59-0.78,23.96-0.78,32.2c0,8.71-6.17-0.09-7.31-1.29',
#         'M36.56,62.66c0.06,0.33,0.11,0.85-0.1,1.32C35.2,66.76,28,72.86,18.15,76.6',
#         'M43.35,70.63c0.07,0.53,0.34,1.42-0.14,2.12c-3.34,4.86-11.07,11.96-24.93,20.3',
#         ####################
#         'M55.82,59.52c2.43,0.94,2.01,0.94,5.57,0.63c7.24-0.63,16.04-2.59,18.25-2.69c4.97-0.22,4.76,1.12,4.76,3.74c0,4.2-0.52,22.99-0.52,31.98c0,9.54-6.53,0.71-7.77,0.15',
#         'M71.78,61.24c0.04,0.32,0.09,0.83-0.09,1.29c-1.06,2.72-7.15,8.69-15.48,12.34',
#         'M79.72,66.99c0.07,0.55,0.14,1.42-0.13,2.22c-1.63,4.67-10.93,15.46-23.68,21.74',
#         ####################
#         ]
# cubic_bezier_params_list = [cubic_bezier_extract(e) for e in d_curve_examples]
# svg_str = svg_str_from_cubic_bezier_params(cubic_bezier_params_list)
# svg_np = svg_str_to_np_image(svg_str)
# save_np_image(add_white_background_trans_image(svg_np), 'svg_np.png')





















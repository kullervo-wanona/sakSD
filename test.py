
from sys import platform
if 'linux' in platform: 
    from IPython.core.debugger import set_trace
    trace = set_trace
elif 'darwin' in platform: #mac os
    import pdb
    trace = pdb.set_trace
else:
    import pdb
    trace = pdb.set_trace

import pprint
pp = pprint.PrettyPrinter(width=41, compact=True).pprint
   
import numpy as np
import os
import pickle
from argparse import ArgumentParser
from pathlib import Path

def main():
    parser = ArgumentParser()
    # parser.add_argument("-d", "--data_dir", default='/Datasets/Kanji/Stroke3/')
    parser.add_argument("-d", "--data_dir", default='/Datasets/Kanji/Stroke6/')
    args = parser.parse_args()

    with open(str(Path.home())+args.data_dir + 'images.npy', 'rb') as f: loaded_images_np = np.load(f)
    with open(str(Path.home())+args.data_dir + 'labels.pickle', 'rb') as f: loaded_labels = pickle.load(f)

    print(loaded_images_np.shape)
    print(len(loaded_labels))


    
    trace()

if __name__ == "__main__":
    main()























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
# trace()






















import os
from argparse import ArgumentParser
import xml.etree.ElementTree as ET
from lib import kanji_dataset as kd

def main():
    # Example call: 
    # python create_dataset --dir='./dataset1/' --stroke=5 --dir='./dataset1/' --stroke=5

    parser = ArgumentParser()
    parser.add_argument("-d", "--dir", default='./dataset/')
    parser.add_argument("-x", "--xml", default='./xml/')
    parser.add_argument("-s", "--stroke", default=3)
    parser.add_argument("-r", "--im_height", default=109)
    parser.add_argument("-w", "--im_width", default=109)
    parser.add_argument("-g", "--svg", default=True)
    args = parser.parse_args()

    kanji_char_entries = list(ET.parse(args.xml + 'kanjidic2.xml').getroot())[1:]
    svg_all_entries = list(ET.parse(args.xml + 'kanjivg-20220427.xml').getroot())
    kanji_metadata_dict, meaning_filtered_metadata_dict = kd.get_kanji_metadata_dict(kanji_char_entries)
    meaning_and_svg_set = kd.filter_meaning_and_svg_hexes(meaning_filtered_metadata_dict, svg_all_entries)
    kd.create_dataset(svg_all_entries, meaning_and_svg_set, args.im_height, args.im_width, args.stroke, 
                      args.dir, kanji_metadata_dict, create_svgs=args.svg)

if __name__ == "__main__":
    main()









































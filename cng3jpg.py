#!/usr/bin/python
"""Convert "Complete National Geographic" CNG files to JPG for use under Linux

cng2jpg.py --src /run/media/user/CNG_DISC1/disc1/images --dst ~/CNG/discs/images
"""

import os
import argparse
import multiprocessing

def convert_one(src_filename, dst_filename, remove=False):
    """Convert source file by performing a byte-by-byte xor 239, save result into new file

    :param src_filename: source filename, will be opened read-only
    :param dst_filename: destination file, will be truncated if exists
    :param remove: if True, remove original .cng file as it is converted. Use if data was
                   already copied from CDs to local drive, to avoid needing extra 48Gb of space.
    """
    print(dst_filename)
    with open(src_filename, 'rb', 524288) as in_stream, open(dst_filename, 'wb', 524288) as out_stream:
        out_stream.write(bytearray((c ^ 239) for c in in_stream.read()))
    if(remove):
        os.remove(src_filename)

def convert_all(src_path, dst_path, remove=False):
    """Recursively convert all .cng files found in src_path.

    Converted .cng files are saved as <file>.jpg under dst_path.
    Intermediary subdirectories will be created as necessary to preserve the directory structure.

    :param src_path: source directory (must exist)
    :param dst_path: target directory, can be same as source (will be created if missing)
    :param remove: if True, remove original .cng files as they are converted. Use if data was
                   already copied from CDs to local drive, to avoid needing extra 48Gb of space.
    """

    pool = multiprocessing.Pool(multiprocessing.cpu_count() * 2)
    
    print("Building list of files for processing")
    joblist = []
 
    for root, dirs, files in os.walk(src_path):
        target_path = root.replace(src_path, dst_path, 1)
        for filename in files:
            basename, ext = os.path.splitext(filename)
            if ext.lower() == '.cng':
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                dst_filename = os.path.join(target_path, basename + ".jpg")
                src_filename = os.path.join(root, filename)
                joblist.append((src_filename,dst_filename))
                    
    pool.starmap(convert_one, joblist)

def main():
    parser = argparse.ArgumentParser(description='Convert NatGeo CNG files to JPG')
    parser.add_argument('-s', '--src', required=True,
                        help='path to source directory containing files to convert')
    parser.add_argument('-d', '--dst', required=False,
                        help='optional destination path (default in-place)')
    parser.add_argument('-r', '--remove', action='store_true', default=False,
                        help='remove original cng files after conversion')
    args = parser.parse_args()

    if args.dst and not os.path.exists(args.dst):
        os.makedirs(args.dst)

    convert_all(args.src, args.dst or args.src, remove=args.remove)


if __name__ == '__main__':
    main()

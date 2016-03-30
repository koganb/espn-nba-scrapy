import argparse
import os

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='data directory', required=True)
    parser.add_argument('--file_prefix', help='Files to merge prefix', required=True)
    parser.add_argument('--remove_merged_files', help='data directory', required=False, default=True, type=bool)
    args = parser.parse_args()


    from os import listdir
    from os.path import isfile, join
    file_list = [f for f in listdir(args.data_dir) if (isfile(join(args.data_dir, f)) and args.file_prefix in str(f) and str(f).endswith('csv') and '_' in str(f))]

    if file_list :
        with open(args.data_dir +'/' + args.file_prefix +'.csv', 'wb') as fout :
            for index, file_name in enumerate(file_list):
                with open(args.data_dir +'/' + file_name, 'rb') as fin :
                    if index != 0:
                        fin.next() # skip the header
                    for line in fin:
                         fout.write(line)

    if args.remove_merged_files:
        for file_name in file_list:
            os.remove(args.data_dir +'/' + file_name)

if __name__ == "__main__":
    main()


import argparse
import re


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract replics from text')
    parser.add_argument('file', help='images to be aligned')
    args = parser.parse_args()

    pattern = re.compile(r'\“([^\”]+?),?\.?\”')
    f = open(args.file)
    for line in f:
        match = pattern.search(line)
        if match:
            replic = match.group(1)
            if len(replic) > 40:
                for s in re.split(r'[;.?!]\s+', replic):
                    print(s)
            else:
                print(replic)


import argparse
import json


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert labels exported from Labelbox')
    parser.add_argument('file', help='Exported file with labels')
    parser.add_argument('--mapping', '-m', default='data/names_mapping.txt', help='mapping of file names and ids')
    parser.add_argument('--output', '-o', default='data/eng_dataset/bboxes.txt')
    args = parser.parse_args()

    with open(args.file) as f:
        labels = json.load(f)

    mapping = {}
    with open(args.mapping) as mapping_file:
        for line in mapping_file:
            name, file_id = line.rstrip().split(' ')
            mapping[file_id] = name

    bboxes = {}
    for row in labels:
        ID = row['ID']
        name = row['External ID']
        if ID in mapping:
            name = mapping[ID]
        bboxes[name] = []
        if len(row['Label']) == 0:
            continue
        for object in row['Label']['objects']:
            # object bounding box
            bboxes[name].append(object['bbox'])
            # object label
            bboxes[name][-1]['label'] = object['value']
    with open(args.output, 'w') as bboxes_file:
        json.dump(bboxes, bboxes_file, indent=4)

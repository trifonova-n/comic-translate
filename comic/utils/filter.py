from comic.utils.bbox import check_intersection_xy


def check_intersections(box, boxes):
    for b in boxes:
        if check_intersection_xy(box, b):
            return True
    return False


def filter_outputs(anns):
    output = []
    for ann in anns:
        items = list(zip(ann['scores'], ann['labels'], ann['boxes'], ann['masks']))
        items.sort(reverse=True)
        out = {'scores': [], 'labels': [], 'boxes': [], 'masks': []}
        for s, l, b, m in items:
            if not check_intersections(b, out['boxes']):
                out['scores'].append(s)
                out['labels'].append(l)
                out['boxes'].append(b)
                out['masks'].append(m)
        output.append(out)
    return output

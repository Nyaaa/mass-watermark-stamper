import argparse
import os
import sys
from PIL import Image, ImageOps


def counter(rootdir_):
    """counting images recursively"""
    file_list = []
    for root, subFolders, files in os.walk(rootdir_):
        for file in files:
            if os.path.splitext(file)[1].lower() in ('.jpg', '.jpeg'):
                img = os.path.join(root, file)
                file_list.append(img)
    return file_list


def stamp_small(dim, stamp):
    """resizing stamp"""
    if dim > 900:
        dim = 900
    scale = (20 * dim) / 10000
    tempstamp_img = Image.open(stamp)
    stamp_width, stamp_height = tempstamp_img.size
    scaled_stamp_w, scaled_stamp_h = int(stamp_width * scale), int(stamp_height * scale)
    tempstamp_img = tempstamp_img.resize((scaled_stamp_w, scaled_stamp_h))
    return tempstamp_img, scaled_stamp_w, scaled_stamp_h


def get_gravity(dim, w, h):
    gravity = results.gravity
    if gravity == "n": return (dim - w) // 2, 0
    elif gravity == "ne": return (dim - w), 0
    elif gravity == "nw": return 0, 0
    elif gravity == "s": return (dim - w) // 2, (dim - h)
    elif gravity == "se": return (dim - w), (dim - h)
    elif gravity == "sw": return 0, (dim - h)
    elif gravity == "e": return (dim - w), (dim - h) // 2
    elif gravity == "w": return 0, (dim - h) // 2
    elif gravity == "c": return int(dim / 2 - w / 2), int(dim / 2 - h / 2)


def start():

    path = results.folder
    stamp = results.stamp
    rootdir = path[0]
    application_path = os.path.dirname(os.path.realpath(sys.argv[0]))

    number = 1
    total = len(counter(rootdir))

    if not stamp:
        stamp = os.path.join(application_path, "stamp.png")
    if os.path.exists(stamp):
        print("Using stamp:", stamp)
    else:
        print("No stamp found")

    for file in counter(rootdir):
        thisfile = os.path.abspath(file)
        file_dir = os.path.dirname(thisfile)
        os.chdir(file_dir)
        if not os.path.exists('./stamp'): os.makedirs('./stamp')
        print(f'Processing file {number} out of {total}')
        newfile = "./stamp/%03d.jpg" % number

        with Image.open(file) as img_:
            img_.load()

        # crop
        invert_img = ImageOps.invert(img_)
        image_box = invert_img.getbbox()
        cropped_img = img_.crop(image_box)

        wid, hei = cropped_img.size
        dim = max(wid, hei)
        dim = 5 * round(dim / 5)

        # square
        square_img = Image.new('RGB', (dim, dim), (255, 255, 255, 0))
        square_img.paste(cropped_img, (int((dim - wid) / 2), int((dim - hei) / 2)))

        # resize files over 900 pixels
        if dim > 900:
            dim = 900
            square_img = square_img.resize((dim, dim))

        # stamping
        if os.path.exists(stamp):
            tempstamp, scaled_stamp_w, scaled_stamp_h = stamp_small(dim, stamp)  # call resizer
            square_img.paste(tempstamp, get_gravity(dim, scaled_stamp_w, scaled_stamp_h), tempstamp)
        square_img.save(newfile)
        number += 1

    print("Done!")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gravity', action='store', dest='gravity', help='tells where to put a stamp', nargs='?',
                        default='se', choices=['n', 's', 'e', 'w', 'nw', 'sw', 'ne', 'se', 'c'])
    parser.add_argument('-f', '--folder', action='store', dest='folder', help='folder to process', nargs=1,
                        required=True)
    parser.add_argument('-s', '--stamp', action='store', dest='stamp', help='path to your stamp', nargs='?',
                        default=False)
    results = parser.parse_args()

    start()

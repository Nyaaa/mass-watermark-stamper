import os
import sys
from PIL import Image, ImageOps
from gooey import Gooey, GooeyParser
import ctypes
import platform


def counter(path):
    """counting images recursively"""
    file_list = []
    for root, subFolders, files in os.walk(path):
        for file in files:
            if os.path.splitext(file)[1].lower() in ('.jpg', '.jpeg'):
                img = os.path.join(root, file)
                file_list.append(img)
    return file_list


def stamp_small(dim, stamp):
    """resizing stamp"""
    v_size = int(dim * 0.2)
    temp_stamp_img = Image.open(stamp)

    scale = (v_size / float(temp_stamp_img.size[1]))
    h_size = int((float(temp_stamp_img.size[0]) * float(scale)))
    temp_stamp_img = temp_stamp_img.resize((h_size, v_size))
    return temp_stamp_img, h_size, v_size


def get_gravity(gravity, dim, w, h):
    if gravity == "n": return (dim - w) // 2, 0
    elif gravity == "ne": return (dim - w), 0
    elif gravity == "nw": return 0, 0
    elif gravity == "s": return (dim - w) // 2, (dim - h)
    elif gravity == "se": return (dim - w), (dim - h)
    elif gravity == "sw": return 0, (dim - h)
    elif gravity == "e": return (dim - w), (dim - h) // 2
    elif gravity == "w": return 0, (dim - h) // 2
    elif gravity == "c": return int(dim / 2 - w / 2), int(dim / 2 - h / 2)


if len(sys.argv) >= 2:
    """If any arguments are passed, run in CLI mode,
    otherwise run in GUI mode"""
    if '--ignore-gooey' not in sys.argv:
        sys.argv.append('--ignore-gooey')


@Gooey(program_name="Mass watermark stamper",
       progress_regex=r"^Processing file (?P<current>\d+) out of (?P<total>\d+)$",
       progress_expr="current / total * 100")
def start():
    application_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    stamp = os.path.join(application_path, "stamp.png")

    parser = GooeyParser()
    parser.add_argument('-g', '--gravity', action='store', dest='gravity', help='Where to put a stamp', nargs='?',
                        default='se', choices=['n', 's', 'e', 'w', 'nw', 'sw', 'ne', 'se', 'c'])
    parser.add_argument('-l', '--limit', action='store', dest='limit', help='Max image size, px', nargs='?',
                        default=900, type=int)
    parser.add_argument('-f', '--folder', action='store', dest='folder', help='Folder to process', nargs=1,
                        required=True, widget='DirChooser')
    parser.add_argument('-s', '--stamp', action='store', dest='stamp', help='Path to your stamp', nargs='?',
                        default=stamp, widget='FileChooser')
    results = parser.parse_args()

    stamp = results.stamp
    limit = results.limit
    root_dir = results.folder[0]
    number = 1
    file_fist = counter(root_dir)
    total = len(file_fist)

    if os.path.exists(stamp):
        print("Using stamp:", stamp)
    else:
        print("No stamp found")

    for file in file_fist:
        file_dir = os.path.dirname(file)
        output_dir = os.path.join(file_dir, "stamp")
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        print(f'Processing file {number} out of {total}')
        newfile = os.path.join(output_dir, "%03d.jpg" % number)

        with Image.open(file) as source_img:
            source_img.load()

        # crop
        invert_img = ImageOps.invert(source_img)
        image_box = invert_img.getbbox()
        cropped_img = source_img.crop(image_box)

        wid, hei = cropped_img.size
        dim = max(wid, hei)
        dim = 5 * round(dim / 5)

        # square
        square_img = Image.new('RGB', (dim, dim), (255, 255, 255, 0))
        square_img.paste(cropped_img, (int((dim - wid) / 2), int((dim - hei) / 2)))

        # resize files over 900 pixels
        if dim > limit:
            dim = limit
            square_img = square_img.resize((dim, dim))

        # stamping
        if os.path.exists(stamp):
            temp_stamp, scaled_stamp_w, scaled_stamp_h = stamp_small(dim, stamp)  # call resizer
            square_img.paste(temp_stamp, get_gravity(results.gravity, dim, scaled_stamp_w, scaled_stamp_h), temp_stamp)
        square_img.save(newfile)
        number += 1

    print("Done!")


if __name__ == '__main__':
    if platform.system() == "Windows":
        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
    start()

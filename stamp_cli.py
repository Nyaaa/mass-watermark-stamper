#!/usr/bin/python
# -*- coding: utf-8 -*- 
import argparse
import contextlib
import os
import re
import subprocess
import sys
import tempfile

# parsing arguments ---------------------
parser = argparse.ArgumentParser()
parser.add_argument('-g', '--gravity', action='store', dest='gravity', help='tells where to put a stamp', nargs='?', default='se', choices=['n', 's', 'e', 'w', 'nw', 'sw', 'ne', 'se', 'c'])
parser.add_argument('-f', '--folder', action='store', dest='folder', help='folder to process', nargs=1, required=True)
parser.add_argument('-s', '--stamp', action='store', dest='stamp', help='path to your stamp', nargs='?', default=False)
results = parser.parse_args()

path = results.folder
stamp = results.stamp
rootdir = path[0]

# ---------------------------------------
number = 1
fileList = []
temp = tempfile.TemporaryFile()
stamp_name = "stamp.png"

application_path = os.path.dirname(os.path.realpath(sys.argv[0]))
if not stamp:
    stamp = os.path.join(application_path, stamp_name)
if os.path.exists(stamp):
    print("Using stamp:", stamp)
else:
    print("No stamp found")

# interpret gravity argument------------
grav = dict(n='North', s='South', e='East', w='West', nw='NorthWest', sw='SouthWest', ne='NorthEast', se='SouthEast',
            c='Center')
gravity = grav.get(results.gravity)

# muting stdout-------------------------
class DummyFile(object):
    def write(self, x): pass

@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout

# counting images recursively----------
for root, subFolders, files in os.walk(rootdir):
    for file in files:
        if os.path.splitext(file)[1].lower() in ('.jpg', '.jpeg'):
            f = os.path.join(root,file)
            fileList.append(file)
total = len(fileList)

def round_step(number, multiple):
    return multiple * round(number / multiple)


def stamp_small(dim):
    """resizing stamp
    size = % of final dimension (dim)"""
    scale = 55
    if dim > 900:
        scale = 25
    elif 900 <= dim < 700:
        scale = 40
    elif 700 <= dim < 400:
        scale = 65
    stampsize = int(dim/100*scale)
    stampsize = round_step(stampsize, 5)
    tempstamp = sys.path[0] + "\\tempstamp.png"
    os.system('magick convert %s -resize %d %s' % (stamp, stampsize, tempstamp))
    return tempstamp


################
### resizing ###
################
for root, subdirs, files in os.walk(rootdir):  # recursion
    for file in files:
        if os.path.splitext(file)[1].lower() in ('.jpg', '.jpeg'):
            img = os.path.join(root, file)
            img = "%s" % img
            #print(img)
            fileList.append(img)
            os.chdir(root)
            if not os.path.exists('.\stamp'): os.makedirs('.\stamp')
            print(f'Processing file {number} out of {total}')
        # get width
            wid = subprocess.Popen(['magick', 'identify', '-format', '%w', '%s' % img], shell=True, stdout=subprocess.PIPE)
            wid = str(wid.communicate())
            wid = int(re.sub("\D", "", wid))  # \D removes any non-digit character
        # get height
            hei = subprocess.Popen(['magick', 'identify', '-format', '%h', '%s' % img], shell=True, stdout=subprocess.PIPE)
            hei = str(hei.communicate())
            hei = int(re.sub("\D", "", hei))  # \D removes any non-digit character

            if wid > hei:
                dim = wid
            else:
                dim = hei
            dim = round_step(dim, 5)

            newfile = ".\stamp\%03d.jpg" % number
        # square
            os.system(f'magick convert {img} -background white -gravity center -extent {dim}x{dim} {newfile}')
        # resize files over 900 pixels
            if dim > 900: os.system(f'magick convert {newfile} -resize 900 {newfile}')
        # stamping
            if os.path.exists(stamp):
                tempstamp = stamp_small(dim)  # call resizer
                os.system(f'magick composite -gravity {gravity} {tempstamp} {newfile} {newfile}')
                os.remove(tempstamp)
            number = number + 1
print("Done!")

from PIL import Image, ImageDraw
import datetime
import numpy, cv2
import subprocess, os
from shutil import copyfile

DOT_WIDTH = 1
DOT_HEIGHT = 1
DOT_HSPACE = 1
DOT_VSPACE = 1

BORDER_THICKNESS = 1
BORDER_HSPACE = 2
BORDER_VSPACE = 2

PAD_WIDTH = 8
PAD_HEIGHT = 8

SCALE_IMG = 16
SCALE_VID = 4

# in number of dots
GRID_WIDTH = 52
GRID_HEIGHT = 80

BATTERY_WIDTH = GRID_WIDTH*DOT_WIDTH + (GRID_WIDTH*DOT_HSPACE - 1) + BORDER_HSPACE + BORDER_HSPACE + 2*BORDER_THICKNESS
BATTERY_HEIGHT = GRID_HEIGHT*DOT_HEIGHT + (GRID_HEIGHT*DOT_VSPACE - 1) + BORDER_VSPACE + BORDER_VSPACE + 2*BORDER_THICKNESS

TERMINAL_WIDTH = round(1/3 * BATTERY_WIDTH)
TERMINAL_HEIGHT = round(1/4 * TERMINAL_WIDTH)

CANVAS = (BATTERY_WIDTH, BATTERY_HEIGHT)

WHITE = 3*(255,)
GREY = 3*(8,)


def get_DOB():
    # year, month, day = int(input("YYYY: ")), int(input("MM: ")), int(input("DD: "))
    year, month, day = 1999, 3, 26
    return datetime.date(year, month, day)

def calculate_fill(birth):
    today = datetime.datetime.date(datetime.datetime.now())
    years_alive = (today.year - birth.year)

    birthday = datetime.date(today.year, birth.month, birth.day)
    days_until_birthday = (birthday - today).days

    # subracting a boolean to get the behaviour of 0->0 else x->1
    return 52*years_alive - days_until_birthday//7 - (days_until_birthday%7 != 0)

def generate_image(fill_count):
    im = Image.new("RGB", CANVAS)
    draw = ImageDraw.Draw(im)

    draw.rectangle([0, 0, im.width, BORDER_THICKNESS-1], fill=WHITE)
    draw.rectangle([0, im.height-1, im.width-1, im.height-BORDER_THICKNESS], fill=WHITE)
    draw.rectangle([0, 0, BORDER_THICKNESS-1, im.height], fill=WHITE)
    draw.rectangle([im.width-1, 0, im.width-BORDER_THICKNESS, im.height-BORDER_THICKNESS], fill=WHITE)

    px = im.load()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if 52*y + x < fill_count:
                px[BORDER_THICKNESS + BORDER_HSPACE + (DOT_WIDTH + DOT_HSPACE)*x, BORDER_THICKNESS + BORDER_VSPACE + (DOT_HEIGHT + DOT_VSPACE)*y] = GREY
            else:
                px[BORDER_THICKNESS + BORDER_HSPACE + (DOT_WIDTH + DOT_HSPACE)*x, BORDER_THICKNESS + BORDER_VSPACE + (DOT_HEIGHT + DOT_VSPACE)*y] = WHITE

    temp = Image.new("RGB", (im.width, im.height + TERMINAL_HEIGHT))
    temp.paste(im, (0, TERMINAL_HEIGHT))
    im = temp

    draw = ImageDraw.Draw(im)
    draw.rectangle([round((im.width - TERMINAL_WIDTH)/2), 0, im.width - TERMINAL_WIDTH, TERMINAL_HEIGHT], fill=WHITE)

    temp = Image.new("RGB", (im.width + 2*PAD_WIDTH, im.height + 2*PAD_HEIGHT))
    temp.paste(im, (PAD_WIDTH, PAD_HEIGHT))
    im = temp

    return im

def four_digits(num):
    return (4-len(str(num)))*"0" + str(num)

def generate_video(filename):
    im = generate_image(0)

    size = (im.width*SCALE_VID, im.height*SCALE_VID)
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')

    video = cv2.VideoWriter(filename, fourcc, 52, size)
    video.write(cv2.cvtColor(numpy.array(im.resize(size)), cv2.COLOR_RGB2BGR))

    px = im.load()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            px[BORDER_THICKNESS + BORDER_HSPACE + (DOT_WIDTH + DOT_HSPACE)*x + PAD_WIDTH, BORDER_THICKNESS + BORDER_VSPACE + (DOT_HEIGHT + DOT_VSPACE)*y + PAD_HEIGHT + TERMINAL_HEIGHT] = GREY
            video.write(cv2.cvtColor(numpy.array(im.resize(size)), cv2.COLOR_RGB2BGR))

    video.release()

def compress_video(filename, quality):
    copy = "temp.mp4"
    copyfile(filename, copy)
    subprocess.call("ffmpeg -i %s -vcodec libx264 -crf %i %s -y" % (copy, quality, filename))
    os.remove(copy)

im = generate_image(calculate_fill(get_DOB()))
im = im.resize((i*SCALE_IMG for i in im.size))

# im.show()
im.save("life-charge.png", "PNG")

generate_video("life-charge.mp4")
compress_video("life-charge.mp4", 16)
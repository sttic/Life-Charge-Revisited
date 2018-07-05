from PIL import Image, ImageDraw
import datetime
import numpy, cv2
import subprocess, os
from shutil import copyfile

DOT_WIDTH, DOT_HEIGHT = 1, 1
DOT_HSPACE, DOT_VSPACE = 1, 1

BORDER_THICKNESS = 1
BORDER_HSPACE, BORDER_VSPACE = 2, 2

PAD_WIDTH, PAD_HEIGHT = 8, 8

SCALE_IMG, SCALE_VID = 16, 4

GRID_WIDTH, GRID_HEIGHT = 52, 80

BATTERY_WIDTH = GRID_WIDTH*DOT_WIDTH + (GRID_WIDTH - 1)*DOT_HSPACE + 2*BORDER_HSPACE + 2*BORDER_THICKNESS
BATTERY_HEIGHT = GRID_HEIGHT*DOT_HEIGHT + (GRID_HEIGHT - 1)*DOT_VSPACE + 2*BORDER_VSPACE + 2*BORDER_THICKNESS

TERMINAL_WIDTH = round(min(1/3 * BATTERY_WIDTH, 1/4 * BATTERY_HEIGHT))
TERMINAL_HEIGHT = round(min(1/10 * BATTERY_WIDTH, 1/16 * BATTERY_HEIGHT))

BODY_SIZE = (BATTERY_WIDTH, BATTERY_HEIGHT)

WHITE, GREY, BLACK = 3*(255,), 3*(8,), 3*(0,)



def get_DOB():
    year, month, day = int(input("YYYY: ")), int(input("MM: ")), int(input("DD: "))
    # year, month, day = 1999, 3, 26
    return datetime.date(year, month, day)

def calculate_fill(birth):
    today = datetime.datetime.date(datetime.datetime.now())
    years_alive = (today.year - birth.year)

    birthday = datetime.date(today.year, birth.month, birth.day)
    days_until_birthday = (birthday - today).days

    # subracting a boolean to get the behaviour of 0->0 else x->1
    return 52*years_alive - days_until_birthday//7 - (days_until_birthday%7 != 0)

def generate_image(fill_count):
    im = Image.new("RGB", BODY_SIZE)
    draw = ImageDraw.Draw(im)

    draw.rectangle([0, 0, im.width, BORDER_THICKNESS-1], fill=WHITE)
    draw.rectangle([0, im.height-1, im.width-1, im.height-BORDER_THICKNESS], fill=WHITE)
    draw.rectangle([0, 0, BORDER_THICKNESS-1, im.height], fill=WHITE)
    draw.rectangle([im.width-1, 0, im.width-BORDER_THICKNESS, im.height-BORDER_THICKNESS], fill=WHITE)

    px = im.load()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WHITE
            if 52*y + x < fill_count:
                color = GREY
            pos = (BORDER_THICKNESS + BORDER_HSPACE + (DOT_WIDTH + DOT_HSPACE)*x, BORDER_THICKNESS + BORDER_VSPACE + (DOT_HEIGHT + DOT_VSPACE)*y)
            if DOT_WIDTH > 1 or DOT_HEIGHT > 1:
                draw.rectangle(pos + (pos[0] + DOT_WIDTH - 1, pos[1] + DOT_HEIGHT - 1))
            else:
                # problems with drawing rectangle of size 1 pixel
                px[pos[0], pos[1]] = color

    temp = Image.new("RGB", (im.width, im.height + TERMINAL_HEIGHT))
    temp.paste(im, (0, TERMINAL_HEIGHT))
    im = temp

    draw = ImageDraw.Draw(im)
    draw.rectangle([round((im.width - TERMINAL_WIDTH)/2), 0, round((im.width + TERMINAL_WIDTH)/2), TERMINAL_HEIGHT], fill=WHITE)

    temp = Image.new("RGB", (im.width + 2*PAD_WIDTH, im.height + 2*PAD_HEIGHT))
    temp.paste(im, (PAD_WIDTH, PAD_HEIGHT))
    im = temp

    return im

def generate_video(filename):
    im = generate_image(0)

    size = (im.width*SCALE_VID, im.height*SCALE_VID)
    # TODO use openh264
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

def generate_frames(filepath, scale):
    im = generate_image(0)

    im2 = im.resize((i*scale for i in im.size))
    im2.save(filepath + '/life-charge-{:04d}.png'.format(0), 'PNG')

    px = im.load()
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            px[BORDER_THICKNESS + BORDER_HSPACE + (DOT_WIDTH + DOT_HSPACE)*x + PAD_WIDTH, BORDER_THICKNESS + BORDER_VSPACE + (DOT_HEIGHT + DOT_VSPACE)*y + PAD_HEIGHT + TERMINAL_HEIGHT] = GREY
            im2 = im.resize((i*scale for i in im.size))
            im2.save(filepath + '/life-charge-{:04d}.png'.format(GRID_WIDTH*y + x + 1), 'PNG')

im = generate_image(calculate_fill(get_DOB()))
im = im.resize((i*SCALE_IMG for i in im.size))

# im.show()
im.save("life-charge.png", "PNG")

# generate_video("life-charge.mp4")
# compress_video("life-charge.mp4", 16)
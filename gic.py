# ------------------------------------------------------------
#         _                      _  __   _                                   _      
#    __ _(_) ___            __ _(_)/ _| (_)_ __     ___ ___  _ __  ___  ___ | | ___ 
#   / _` | |/ __|  _____   / _` | | |_  | | '_ \   / __/ _ \| '_ \/ __|/ _ \| |/ _ \
#  | (_| | | (__  |_____| | (_| | |  _| | | | | | | (_| (_) | | | \__ \ (_) | |  __/
#   \__, |_|\___|          \__, |_|_|   |_|_| |_|  \___\___/|_| |_|___/\___/|_|\___|
#   |___/                  |___/                                                       
#                        
# gic - gif in console, play char gif in console via python
# - requirements: python3, Pillow==6.1.0
# - basic usage: `python gic.py test.gif`
# - options: use `python gic.py -h` for help
# - by bunnyxt, 2020-11-17, license: GPL v3
# - https://github.com/bunnyxt/gic
# ------------------------------------------------------------

from PIL import Image, ImageSequence
import sys
import time
import os
import argparse


char_array_dict = {
    16: [' ', ':', '-', '?', 'l', 'J', 'å', 'k', '9', '8', 'Ä', 'Ü', 'Ö', 'N', 'W', 'M'],
}

def analyseImage(image):
    results = {
        'size': image.size,
        'mode': 'full',
    }
    try:
        while True:
            if image.tile:
                tile = image.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != image.size:
                    results['mode'] = 'partial'
                    break
            image.seek(image.tell() + 1)
    except EOFError:
        pass
    return results


def get_frames(image):
    mode = analyseImage(image)['mode']
    p = image.getpalette()
    last_frame = image.convert('RGBA')
    frames = []

    try:
        while True:
            if not image.getpalette():
                image.putpalette(p)

            new_frame = Image.new('RGBA', image.size)
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(image, (0, 0), image.convert('RGBA'))
            #new_frame.save('%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), count), 'PNG')
            # new_frame.show()
            frames.append(new_frame)

            last_frame = new_frame
            image.seek(image.tell() + 1)
    except EOFError:
        pass

    return frames


def get_durations(image):
    durations = []
    for frame in ImageSequence.Iterator(image):
        durations.append(frame.info['duration'])
    return durations


def get_char_array(char_array_size):
    if char_array_size not in char_array_dict.keys():
        raise RuntimeError('%d size of char array not support' % char_array_size)
    return char_array_dict[char_array_size]


def get_terminal_window_size():
    return map(lambda x: int(x), os.popen('stty size', 'r').read().split())


def calc_display_size(image_x, image_y, window_x, window_y, block_ratio):
    # expand x
    image_x = int(image_x * block_ratio)
    
    # remove bottom row
    window_y -= 1

    # 01 try scale height
    scale_ratio = 1 if image_y / window_y < 1 else image_y / window_y
    display_rows = image_y if scale_ratio == 1 else window_y
    display_cols = int(image_x * scale_ratio)
    if display_cols > window_x:
        # 02 try scale width
        scale_ratio = 1 if image_x / window_x < 1 else image_x / window_x
        display_cols = image_x if scale_ratio == 1 else window_x
        display_rows = int(image_y / scale_ratio)
        if display_rows > window_y:
            # 03 try scale rows and width
            scale_ratio =  window_y / display_rows
            display_rows = int(display_rows * scale_ratio)
            display_cols = int(display_cols * scale_ratio)
    
    return display_rows, display_cols


def calc_char_frames(frames, display_rows, display_cols, char_array, char_array_size, top_empty_rows):
    char_frames = []

    for frame in frames:
        # convert to gray mode
        frame = frame.convert('L')

        # resize frame
        frame = frame.resize((display_cols, display_rows))

        # load frame pixel matrix
        frame_pixel_matrix = frame.load()

        # pixel to char
        char_frame_rows = []
        for i in range(top_empty_rows):
            char_frame_rows.append('')
        for i in range(display_rows):
            char_row = ''
            for j in range(display_cols):
                point = frame_pixel_matrix[j, i]
                level = int(point / char_array_size)
                char_row += char_array[level]
            char_frame_rows.append(char_row)
        char_frames.append(char_frame_rows)
    
    return char_frames


def print_frame(char_frame):
    for char_frame_row in char_frame:
        print(char_frame_row)


def main():
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='show verbose log when running',
    )
    parser.add_argument(
        '-t', '--top-empty-rows', 
        action='store_true',
        help='enable frame top empty rows',
        default=True,
    )
    parser.add_argument(
        '-s', '--size', 
        type=int,
        help='char array size, only support 16 now',
        default=16,
    )
    parser.add_argument(
        '-r', '--ratio', 
        type=float,
        help='char block height / width ratio',
        default=2,
    )
    parser.add_argument(
        'filename', 
        type=str, 
        help='gif filename',
    )
    args = parser.parse_args()

    verbose = args.verbose
    enable_top_empty_rows = args.top_empty_rows
    char_array_size = args.size
    block_ratio = args.ratio
    filename = args.filename
    
    try:
        # load image
        image = Image.open(filename)
        if verbose:
            print('file %s loaded' % filename)

        # check format
        if image.format != 'GIF':
            if verbose:
                print('file format is %s' % image.format)
            raise RuntimeError('input file is %s format, not gif' % image.format)
        
        # get image size
        image_x, image_y = image.size
        if verbose:
            print('image size %d * %d' % (image_x, image_y))
        
        # get frames
        frames = get_frames(image)
        if verbose:
            print('%d frames get' % len(frames))

        # get durations
        durations = get_durations(image)
        if verbose:
            print('%d durations get' % len(durations))
        
        # load char array
        char_array = get_char_array(char_array_size)
        if verbose:
            print('char array with size %d loaded' % char_array_size)

        # display loop
        char_frames = []
        begin_frame_index = 0
        terminal_rows, terminal_cols = 0, 0
        while True:
            # check now terminal window size
            terminal_rows_now, terminal_cols_now = get_terminal_window_size()
            if terminal_rows_now != terminal_rows or terminal_cols_now != terminal_cols:
                # update terminal window size
                terminal_rows, terminal_cols = terminal_rows_now, terminal_cols_now
                # calc display_rows and display_cols
                display_rows, display_cols = calc_display_size(image_x, image_y, terminal_cols, terminal_rows, block_ratio)
                if verbose:
                    print('display size %d * %d' % (display_cols, display_rows))
                # calc top empty rows
                top_empty_rows = 0
                if enable_top_empty_rows:
                    top_empty_rows = terminal_rows - display_rows - 1
                # calc char frames
                char_frames = calc_char_frames(frames, display_rows, display_cols, char_array, char_array_size, top_empty_rows)
                if verbose:
                    print('char frames prepared')

            # print frames
            for index, char_frame in enumerate(char_frames):
                if index < begin_frame_index:
                    # skip frames
                    continue
                elif index == begin_frame_index:
                    # reset begin frame index
                    begin_frame_index = 0
                
                # check now terminal window size
                terminal_rows_now, terminal_cols_now = get_terminal_window_size()
                if terminal_rows_now != terminal_rows or terminal_cols_now != terminal_cols:
                    # need to update char frames, end current gif frame display round immediately
                    begin_frame_index = index
                    break
                
                # print frame
                print_frame(char_frame)

                # duration
                time.sleep(durations[index] / 1000)
            
    except Exception as e:
        if verbose:
            print(e.with_traceback())
        else:
            print(e)
        exit()


if __name__ == "__main__":
    main()

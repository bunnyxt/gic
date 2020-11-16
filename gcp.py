from PIL import Image
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


def get_char_array(char_array_size):
    if char_array_size not in char_array_dict.keys():
        raise RuntimeError('%d size of char array not support' % char_array_size)
    return char_array_dict[char_array_size]

def main():
    # get terminal window size
    terminal_rows, terminal_cols = os.popen('stty size', 'r').read().split()

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='show verbose log when running',
    )
    parser.add_argument(
        '-s', '--size', 
        type=int,
        help='char array size, only support 16 now',
        default=16,
    )
    parser.add_argument(
        'filename', 
        type=str, 
        help='gif filename',
    )
    args = parser.parse_args()

    verbose = args.verbose
    char_array_size = args.size
    filename = args.filename

    # display_rows and display_cols
    display_rows = 80
    display_cols = 140
    
    try:
        # load image
        image = Image.open(filename)
        if verbose:
            print('file %s loaded' % filename)

        # get frames
        frames = get_frames(image)
        if verbose:
            print('%d frames get' % len(frames))

        # load char array
        char_array = get_char_array(char_array_size)
        if verbose:
            print('char array with size %d loaded' % char_array_size)

        # frame to char matrix
        char_matrixes = []
        for frame in frames:
            # convert to gray mode
            frame = frame.convert('L')

            # resize it
            frame = frame.resize((display_cols, display_rows))
            # frame.show()

            # to char matrix
            frame_matrix = frame.load()
            char_matrix = [[0 for _ in range(display_rows)] for _ in range(display_cols)]
            for j in range(display_cols):
                for k in range(display_rows):
                    point = frame_matrix[j, k]
                    level = int(point / char_array_size)
                    char_matrix[j][k] = level
            char_matrixes.append(char_matrix)

        image.close()

        # display loop
        while True:
            for char_matrix in char_matrixes:
                for i in range(display_rows):
                    for j in range(display_cols):
                        level = char_matrix[j][i]
                        print(char_array[level], end='')
                    print('')
                time.sleep(0.1)

    except Exception as e:
        if verbose:
            print(e.with_traceback())
        else:
            print(e)
        exit()


if __name__ == "__main__":
    main()

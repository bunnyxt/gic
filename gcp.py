from PIL import Image
import sys
import time


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


def main():
    try:
        # file name
        file_name = sys.argv[1]
        #file_name = "test.gif"
    except Exception as e:
        print('Usage: python gcp.py <gif-file-name>')
        exit()

    try:
        # load image
        image = Image.open(file_name)

        # get frames
        frames = get_frames(image)

        char_array = [' ', ':', '-', '?', 'l', 'J',
                      'å', 'k', '9', '8', 'Ä', 'Ü', 'Ö', 'N', 'W', 'M']
        char_matrixes = []

        # frame to char matrix
        for frame in frames:
            # convert to gray mode
            frames[i] = frames[i].convert('L')

            # resize it
            frame = frame.resize((140, 80))
            # frame.show()

            # to char matrix
            frame_matrix = frame.load()
            char_matrix = [[0 for _ in range(80)] for _ in range(140)]
            for j in range(140):
                for k in range(80):
                    point = frame_matrix[j, k]
                    level = int(point / 16)
                    char_matrix[j][k] = level
            char_matrixes.append(char_matrix)

        image.close()

        while True:
            for char_matrix in char_matrixes:
                for i in range(80):
                    for j in range(140):
                        level = char_matrix[j][i]
                        print(char_array[level], end='')
                    print("")
                time.sleep(0.1)

    except Exception as e:
        print(e.with_traceback())
        exit()


if __name__ == "__main__":
    main()

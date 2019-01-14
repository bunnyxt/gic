from PIL import Image

# load image
image = Image.open('test.jpg')

# convert to gray mode
image_gray = image.convert("L")

# resize it
image_gray_r = image_gray.resize((80, 140))
image_gray_r.show()

# to char matrix
# show matrix
image_matrix = image_gray_r.load()
char_array = [' ', ':', '-', '?', 'l', 'J',
              'å', 'k', '9', '8', 'Ä', 'Ü', 'Ö', 'N', 'W', 'M']
for i in range(0, 80):
    for j in range(0, 140):
        point = image_matrix[i, j]
        level = int(point / 16)
        print(char_array[level], end='')
    print("")

image.close()

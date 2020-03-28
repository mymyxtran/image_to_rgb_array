"""@package file_to_rgb_array 
@author Quinn Smith
@date 2020-03-28

This script takes an image an outputs it as a c array compatible with DE1-SoC VGA displays.

Notes: 
    1. If you want the image to fit the screen it should have dimensions X:320, Y:240.
       Otherwise it will be displayed incorrectly.
    2. Note: The type used by this script is "unsigned short int" 
    3. Imageio is a required dependency. Install it using pip or conda. 
    4. There are no promises this is bug free :-)

This script uses imageio for the bulk of the image intake handling.
List of supported image formats can be found on the imageio website
See: https://imageio.readthedocs.io/en/stable/formats.html
"""


import argparse
import imageio
import numpy as np
import sys
import logging

def write_to_carray(num_matrix, array_name, file_path):
    """
    @brief Write a matrix of RGB values to a file as a c array.
    @param num_matrix A matrix of 16 bit 5-6-5 RGB values.
    @param array_name The name of the c array variable
    @param file_path The file where the array will be written to
    """
    var_start = "unsigned short int " + array_name + " [] = {\n\t"
    var_end = "};\n"
    var_values = [] 
    for row in num_matrix:
        for cell in row:
            var_values.append(str(cell))
    
    f = open(file_path, "w")
    f.write("// Auto generated image header file\n")
    f.write(var_start)
    f.write(",\n\t".join(var_values) + "\n")
    f.write(var_end)
    f.close()


def rgb_vec_to_num(vec):
    """
    @brief Given a vector of 8-8-8 RGB values formatted as (R,G,B):
           transform that vector into a single number which represents it's value
           in 5-6-5 RGB. This number is DE1-SoC VGA compatible.
    """
    # Bit shifts to convert to 5-6-5
    r = vec[0] >> 3
    g = vec[1] >> 2
    b = vec[2] >> 3
    # Get a single value
    num = (r << 11) + (g << 5) + (b << 0)
    return num


def load_image_as_rgb(image_path):
    """
    @brief Take an image path and return a 2D array of 24 bit rgb values.
           Image intake is handled by the imageio library.
    """
    im = imageio.imread(image_path)
    y_size = im.shape[0]
    x_size = im.shape[1]
    logging.info("Image has dimensions X:%d Y:%d" % (x_size, y_size))
    arr = np.zeros((im.shape[0],im.shape[1]), dtype=int)
    i = 0
    for im_row in im:
        j = 0
        for vec in im_row:
            arr[i,j] = rgb_vec_to_num(vec)
            j = j + 1
        i = i + 1
    return arr
                

def main():
    """
    @brief main is main.
    """
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    parser = argparse.ArgumentParser(description='Convert an image to a c unsigned short array.')
    parser.add_argument("--image_path", type=str, help="The path of the image. Relative is OK.")
    parser.add_argument("--file_path", type=str, help="The file path where the output header file should go: e.g. example.h. Relative is OK.")
    parser.add_argument("--array_name", type=str, help="The name of the array variable")
    args = parser.parse_args()
    if args.array_name is None or args.file_path is None or args.image_path is None:
        logging.error("Uh oh... here is some help:")
        parser.print_help()
        exit(1)

    image_path = args.image_path 
    file_path = args.file_path
    array_name = args.array_name
    arr = load_image_as_rgb(image_path)
    write_to_carray(arr, array_name, file_path)
    logging.info("Wrote %s in %s from %s" % (array_name, file_path, image_path))

if __name__ == "__main__":
    main() 

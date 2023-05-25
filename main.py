import pathlib
import json
import os
import math
import random
import time
import numpy as np
import cv2

import ColorAnalyzer as ca

# standard settings
preview = True
recache = False
tile_path = "tiles_images/Lukas30Private"
file_extensions = ["jpg", "jpeg", "png"]
source_file = "source.jpg"
input_tile_size = 100
output_tile_size = 10
in_out_ratio = output_tile_size / input_tile_size

def cache_tile_images(origin = "tiles_images/", cache_name ="cache.json"):
    print("Getting paths...")
    imgs_dir = pathlib.Path(origin)
    paths = []
    for extension in file_extensions:
        extension_paths = list(imgs_dir.glob("*\\*." + extension))
        paths = paths + extension_paths
    data = {}

    print("caching found images...")
    for idx, img_path in enumerate(paths):
        img = cv2.imread(str(img_path))
        img = resize_with_ratio(img, output_tile_size)
        img = tilize(img, output_tile_size)
        average_color = ca.get_average_color(img)
        if str(tuple(average_color)) in data:
            data[str(tuple(average_color))].append(str(img_path))
        else:
            data[str(tuple(average_color))] = [str(img_path)]
        print("\r", idx , " of ", len(paths), " images cached.", end='')
    with open(cache_name, "w") as file:
        json.dump(data, file, indent=2, sort_keys=True)
    print("\nCaching done")


def tiles_not_cached():
    return "cache.json" not in os.listdir()


def get_tile_coordinates(x_iteration, y_iteration, tilesize):
    x0 = x_iteration * tilesize
    x1 = x_iteration * tilesize + tilesize
    y0 = y_iteration * tilesize
    y1 = y_iteration * tilesize + tilesize
    return x0, x1, y0, y1


def resize_with_ratio(img, size):
    dim = None
    (h, w) = img.shape[:2]

    if w > h:
        r = size / float(h)
        dim = (int(w * r), size)
    else:
        r = size / float(w)
        dim = (size, int(h * r))
    return cv2.resize(img, dim)


def tilize(img, tile_size):
    (h, w) = img.shape[:2]
    y0 = h//2 - tile_size // 2
    y1 = h//2 + tile_size // 2
    x0 = w//2 - tile_size // 2
    x1 = w//2 + tile_size // 2
    return img[y0:y1, x0:x1]


print ("=== Photomosaic ===")
start_time = time.time()

if recache or tiles_not_cached():
    print ("Started caching process")
    try:
        cache_tile_images(tile_path)
    except Exception as e:
        print("Caching failed with error:\n", e)

# load cached files
with open("cache.json", "r") as file:
    data = json.load(file)

img = cv2.imread(source_file)
img_height, img_width, _ = img.shape
num_tiles_h, num_tiles_w = img_height // input_tile_size, img_width // input_tile_size
img = img[:input_tile_size * num_tiles_h, :input_tile_size * num_tiles_w]

# get tile array
tiles = []
tilized_img = np.zeros((output_tile_size * num_tiles_h,
                       output_tile_size * num_tiles_w, 3), np.uint8)
amount_iterations = num_tiles_h * num_tiles_w
done_iterations = 0
for y in range(0, num_tiles_h):
    for x in range(0, num_tiles_w):
        x0, x1, y0, y1 = get_tile_coordinates(x, y, input_tile_size)
        u0, u1, v0, v1 = get_tile_coordinates(x, y, output_tile_size)

        try:
            average_color = ca.get_average_color(img[y0:y1, x0:x1])
        except Exception:
            continue
        closest_color = ca.get_closest_color(average_color, data.keys())

        tile_path = random.choice(data[str(closest_color)])
        tile_image = cv2.imread(tile_path)
        tile_image = resize_with_ratio(tile_image, output_tile_size)
        tile_image = tilize(tile_image, output_tile_size)

        tilized_img[v0:v1, u0:u1] = tile_image

        done_iterations += 1
        print("\r", done_iterations , " of ", amount_iterations, " tiles done.", end='')

        # if preview:
        #     cv2.imshow("Image", tilized_img)
        #     cv2.waitKey(1)

cv2.imwrite("output.jpg", tilized_img)

end_time = time.time()
total_time = end_time - start_time
print("Photomosaic generated in ", total_time, " seconds.")

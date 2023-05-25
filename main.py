import pathlib
import json
import os
import random
import time
import numpy as np
import cv2
import collections
import ColorAnalyzer as ca

# standard settings
preview = True

file_extensions = ["jpg", "jpeg", "png"]
is_caching_tiles = False
tile_cache_name = "tile_cache.json"
tile_path = "tiles_images/Lukas30Private"

is_caching_source = True
source_cache_name = "source_cache.json"
source_path = "source.jpg"

input_tile_size = 100
output_tile_size = 10
in_out_ratio = output_tile_size / input_tile_size


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


def cache_image(tilesize, img_path="source.jpg", cache_name="source_cache.json"):
    data = []

    img = cv2.imread(img_path)
    img_height, img_width, _ = img.shape
    num_tiles_h, num_tiles_w = img_height // tilesize, img_width // tilesize
    data.append(num_tiles_h)
    data.append(num_tiles_w)

    for y in range(0, num_tiles_h):
        for x in range(0, num_tiles_w):
            x0, x1, y0, y1 = get_tile_coordinates(x, y, tilesize)
            average_color = ca.get_average_color(img[y0:y1, x0:x1])
            cache_key = str(tuple(average_color))
            data.append(cache_key)
    with open(cache_name, "w") as file:
        json.dump(data, file, indent=2, sort_keys=True)
    print("\nCached " + img_path + ".")


def get_tile_image_paths_array(origin="tiles_images/"):
    imgs_dir = pathlib.Path(origin)
    paths = []
    for extension in file_extensions:
        extension_paths = list(imgs_dir.glob("*." + extension))
        paths = paths + extension_paths
        extension_paths = list(imgs_dir.glob("*\\*." + extension))
        paths = paths + extension_paths
    return paths


def cache_tiles(origin="tiles_images/", cache_name="cache.json"):
    paths = get_tile_image_paths_array(origin)
    data = collections.defaultdict(list)

    for idx, img_path in enumerate(paths):
        img = cv2.imread(str(img_path))
        img = resize_with_ratio(img, output_tile_size)
        img = tilize(img, output_tile_size)
        average_color = ca.get_average_color(img, True)
        cache_key = str(tuple(average_color))
        data[cache_key].append(str(img_path))
        print("\r", idx, " of ", len(paths), " images cached.", end='')
    with open(cache_name, "w") as file:
        json.dump(data, file, indent=2, sort_keys=True)
    print("\nCached images in " + origin)


print("=== Photomosaic ===")
start_time = time.time()

if is_caching_tiles or tile_cache_name not in os.listdir():
    print("Started tile caching process...")
    try:
        cache_tiles(tile_path, tile_cache_name)
    except Exception as e:
        print("Tile caching failed with error:\n", e)

if is_caching_source or source_cache_name not in os.listdir():
    print("Started source caching process...")
    try:
        cache_image(input_tile_size, source_path, source_cache_name)
    except Exception as e:
        print("Source caching failed with error:\n", e)

# load cached files
with open(tile_cache_name, "r") as file:
    data_tiles = json.load(file)
with open(source_cache_name, "r") as file:
    data_source = json.load(file)
num_tiles_h, num_tiles_w = data_source[:2]
source_averages = data_source[2:]

# get tile array
tiles = []
tilized_img = np.zeros((output_tile_size * num_tiles_h,
                       output_tile_size * num_tiles_w, 3), np.uint8)
for y in range(0, num_tiles_h):
    for x in range(0, num_tiles_w):
        source_tuple = eval(source_averages[x + y * num_tiles_w])
        closest_color = ca.get_closest_color(source_tuple, data_tiles.keys())

        tile_path = random.choice(data_tiles[str(closest_color)])
        tile_image = cv2.imread(tile_path)
        tile_image = resize_with_ratio(tile_image, output_tile_size)
        tile_image = tilize(tile_image, output_tile_size)

        u0, u1, v0, v1 = get_tile_coordinates(x, y, output_tile_size)
        tilized_img[v0:v1, u0:u1] = tile_image

        print("\r", x + y * num_tiles_w, " of ",
              num_tiles_h * num_tiles_w, " tiles done.", end='')

cv2.imwrite("output.jpg", tilized_img)

end_time = time.time()
total_time = end_time - start_time
print("\n\nPhotomosaic generated in ", round(total_time, 2), " seconds.")

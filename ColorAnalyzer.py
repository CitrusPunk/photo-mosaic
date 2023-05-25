import numpy as np
import math

def get_average_color(img):
        average_color = np.average(np.average(img, axis=0), axis=0)
        average_color = np.around(average_color, decimals=-1)
        average_color = tuple(int(i) for i in average_color)
        return average_color

def get_closest_color(color, color_list):
        cr, cg, cb = color

        min_difference = float("inf")
        closest_color = None
        for c in color_list:
            r, g, b = eval(c) # eval color values saved as dict with key (r, g, b)
            difference = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
            if difference < min_difference:
                min_difference = difference
                closest_color = eval(c)

        return closest_color


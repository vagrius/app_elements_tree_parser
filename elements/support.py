from .data import colors_dict_2
import numpy as np
from functools import reduce
from skimage import color

def color_matching(peaked_color):
    hex_rgb_colors = list(colors_dict_2.keys())
    
    r = [int(hex[0:2], 16) for hex in hex_rgb_colors]
    g = [int(hex[2:4], 16) for hex in hex_rgb_colors]
    b = [int(hex[4:6], 16) for hex in hex_rgb_colors]

    # converting colors from list to array (of uint8 elements)
    r = np.asarray(r, np.uint8)
    g = np.asarray(g, np.uint8)
    b = np.asarray(b, np.uint8)

    # stack r, g, b across third dimention - create 3D-array
    rgb = np.dstack((r, g, b))

    # convert from sRGB color spave to LAB color space
    lab = color.rgb2lab(rgb)

    peaked_rgb = np.asarray([int(peaked_color[1:3], 16), int(peaked_color[3:5], 16), int(peaked_color[5:7], 16)], np.uint8)
    peaked_rgb = np.dstack((peaked_rgb[0], peaked_rgb[1], peaked_rgb[2]))
    peaked_lab = color.rgb2lab(peaked_rgb)

    # compute Euclidean distance from peaked_lab to each element of lab
    lab_dist = ((lab[:,:,0] - peaked_lab[:,:,0])**2 + (lab[:,:,1] - peaked_lab[:,:,1])**2 + (lab[:,:,2] - peaked_lab[:,:,2])**2)**0.5

    # get the index of the minimum distance
    min_index = lab_dist.argmin()
    peaked_closest_hex = hex_rgb_colors[min_index]
    peaked_color_name = colors_dict_2[peaked_closest_hex]

    return peaked_closest_hex


def get_element_main_color(colors_names_counter: dict, threshold = 0.75):
    
    if colors_names_counter:
        
        # search if confidence of most rated color is more than treshold
        if list(colors_names_counter.items())[0][1] >= threshold:
            return f"{list(colors_names_counter.items())[0][0]} {list(colors_names_counter.items())[0][1]}"
        
        # otherwise sum confidences of top different colors
        ratios = []
        names = []
        for name, ratio_ in colors_names_counter.items():
            names.append(name)
            ratios.append(ratio_)
            if sum(ratios) >= threshold:
                break
        # and search for general definition for names, e.g. Light Greean, Dark Green == Green
        name_sets = [set(name.split()) for name in names]
        base_name = set.intersection(reduce(lambda s1, s2: s1 & s2, name_sets)) 
        if len(base_name) == 1:
            if not list(base_name)[0] in ("Light", "Dark"):
                return f"{list(base_name)[0]} {sum(ratios)}"

        # if confidences are high enough - this is kind of multicolor   
        if all(map(lambda x: x > threshold / 3, ratios[:3])):
            return "multicolor"

    return "undefined"


def calculate_ratio_from_amount(dict_):
    amount = sum(list(dict_.values()))
    dict_ = {key: round((value / amount), 3) for key, value in sorted(dict_.items(), key=lambda item: item[1], reverse=True)}
    dict_ = {key: value for key, value in dict_.items() if value > 0.001}
    return dict_


def get_element_colors(img):
        colors_counter = {}
        colors_names_counter = {}  
        pixels = list(img.convert('RGB').getdata())
        for r, g, b in pixels:
            color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            colors_counter[color] = colors_counter.get(color, 0) + 1 
        
        # compute ratio for each color
        colors_counter = calculate_ratio_from_amount(colors_counter)
        
        # consolidate via color table
        # VG 03.04.2023 Artem asked to keep 3 main colors as it's hex, not names
        for hex, ratio in colors_counter.items():
            name = color_matching(hex)
            colors_names_counter[name] = round((colors_names_counter.get(name, 0) + ratio), 2)
        colors_names_counter = {f"#{hex.lower()}": ratio for hex, ratio in colors_names_counter.items() if ratio > 0.01}
        result = dict(list(colors_names_counter.items())[:3])

        return result

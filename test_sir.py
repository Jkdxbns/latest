import numpy as np


def derive_time_interval(datax):
    string2 = ''
    datax_array = []
    for a in datax:
        if (a != ','):
            string2 = string2 + a
        else:
            datax_array.append(string2)
            # print(string2)
            string2 = ''
    start = float(datax_array[0])
    stop = float(datax_array[1])
    sample = int(datax_array[2])
    dt = (stop - start) / float(datax_array[2])
    return start, stop, sample, dt


def Convert(lst):
    it = iter(lst)
    res_dct = dict(zip(it, it))
    return res_dct


def zero_crossing(xax_array, yax_array):
    reverse_yax_array = yax_array[::-1]
    reverse_xax_array = xax_array[::-1]
    centre = np.argmax(yax_array)
    left = xax_array[centre]
    right = xax_array[centre]
    for index, value in enumerate(yax_array):
        if (value != 0):
            # print("Left", xax_array[index])
            left = xax_array[index]
            break
        else:
            continue
    for index, value in enumerate(reverse_yax_array):
        if (value != 0):
            # print("Left", reverse_xax_array[index])
            right = reverse_xax_array[index]
            break
        else:
            continue
    return left, right


def convert_string_to_data(data):
    num_array = []
    string1 = ''
    for a in data:
        if (a != ','):
            string1 = string1 + a
        else:
            num_array.append(float(string1))
            string1 = ''
    return num_array


def conv_time_to_filename(start_time):
    fname1 = str(start_time)
    disallowed_characters = " -:"
    for character in disallowed_characters:
        fname2 = fname1.replace(character, "")
    fname = fname2 + '.txt'
    return fname


def derive_area(num_array):
    left = 0
    right = 0
    centre = np.argmax(num_array)
    # print(centre)
    if (num_array[centre] < 0.001):
        new_array1 = 0
    else:
        min = centre
        while (num_array[min] > 0.001):
            # print(min)
            if (min == 2):
                break
            min = min - 1

        left = min
        # print(left)
        max = centre
        while (num_array[max] > 0.001):
            # print(max)
            if (max == (len(num_array) - 2)):
                break
            max = max + 1
        right = max
        new_array = num_array[left:right]
        new_array1 = np.round(np.trapz(new_array, dx=1), 2)
    return new_array1, left, right


def derive_area1(y_array, x_array):
    left = 0
    right = 0
    centre = np.argmax(y_array)
    # print(centre)
    if (y_array[centre] < 0.001):
        new_array1 = 0
    else:
        min = centre
        while (y_array[min] > 0.0001):
            # print(min)
            if (min == 2):
                break
            min = min - 1

        left = x_array[min]
        # print(left)
        max = centre
        while (y_array[max] > 0.0001):
            # print(max)
            if (max == (len(y_array) - 2)):
                break
            max = max + 1
        right = x_array[max]
        y_new_array1 = y_array[min:max]
        x_new_array1 = x_array[min:max]
        area = np.trapz(y_new_array1, x_new_array1)
    return area, left, right

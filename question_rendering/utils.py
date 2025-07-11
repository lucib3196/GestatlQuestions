import math
import random
import copy

arr = [1, 2, 3, 4, 5]


def shuffle_array(arr):
    array = arr[:]
    n = len(array)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        array[i], array[j] = array[j], array[i]  # Swap
    return array


print(shuffle_array(arr))

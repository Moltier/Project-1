import random


def cp(code, *args):
    print("Checkpoint: ", code, end='')
    for x in args:
        print(' | ', x, end='')
    print()


def random_samples(item_list, weight_list, number_of_samples):
    return_list = []
    while number_of_samples > 0:
        choosen = random.choices(item_list, weight_list)
        index = item_list.index(choosen[0])
        item_list.pop(index)
        weight_list.pop(index)
        number_of_samples -= 1
        return_list.extend(choosen)
    return return_list

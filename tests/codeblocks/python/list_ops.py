def append(list1, list2):
    for item in list2:
        list1.append(item)
    return list1


def concat(lists):
    result = []
    for list in lists:
        result = append(result, list)
    return result


def filter(function, list):
    return [item for item in list if function(item)]


def length(list):
    count = 0
    for _ in list:
        count += 1
    return count


def map(function, list):
    return [function(item) for item in list]


def foldl(function, list, initial):
    result = initial
    for item in list:
        result = function(result, item)
    return result


def foldr(function, list, initial):
    result = initial
    for item in reverse(list):
        result = function(item, result)
    return result


def reverse(list):
    return list[::-1]
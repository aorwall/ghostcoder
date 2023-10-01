def foldr(function, list, initial):
    if not list:
        return initial
    return function(list[0], foldr(function, list[1:], initial))
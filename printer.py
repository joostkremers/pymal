from mal_types import *


def pr_str(obj, print_readably=False):
    if type(obj) is list:
        str_list = [pr_str(s, print_readably) for s in obj]
        return '(' + ' '.join(str_list) + ')'

    elif type(obj) is MalVector:
        str_list = [pr_str(s, print_readably) for s in obj.value]
        return '[' + ' '.join(str_list) + ']'

    elif type(obj) is dict:
        str_list = []
        for key, value in obj.items():
            str_list += [pr_str(key, print_readably),
                         pr_str(value, print_readably)]
        return '{' + ' '.join(str_list) + '}'

    elif type(obj) is str:
        string = obj
        if print_readably:
            string = string.replace('\\', r'\\')
            string = string.replace('\n', r'\n')
            string = string.replace('"', r'\"')
            string = '"' + string + '"'
        return string

    elif isinstance(obj, MalError):
        return (pr_str(obj.error, print_readably) + ": " +
                pr_str(obj.descr, print_readably))

    # If none of the above:
    else:
        return str(obj)

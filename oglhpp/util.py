
def is_capitalized(value):
    if value == '':
        return False

    state = 0   # 0: uppercase part. 1: lowercase part

    for ch in value:
        if state == 0:
            if str.isupper(ch):
                state = 1
            else:
                return False
        elif state == 1:
            if str.isupper(ch):
                continue
            elif str.islower(ch):
                state = 2
            else:
                return False
        elif state == 2:
            if not str.islower(ch):
                return False
            
    return True

def split_capitalized(value):
    entries = [] 

    current = ''
    current_i = 0
    for i in range(len(value)):
        ch = value[i]

        if is_capitalized(current) and not is_capitalized(current + ch):
            entries.append(current)
            current = ''
            current_i = i
        
        current += ch

    entries.append(value[current_i:])

    return entries

def camel_case(class_name):
    return ''.join([ item.title() for item in class_name.split(' ')])


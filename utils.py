def string_to_list(string):
    string = string.strip()
    string = string[1:-1]
    friends = string.split('] [')
    friends = [friend.split(' ') for friend in friends]
    return friends

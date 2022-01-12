def string_to_list(string):
    string = string.strip()
    if not string:
        return []
    string = string[1:-1]
    friends = string.split('] [')
    friends = [friend.split(' ') for friend in friends]
    for idx in range(len(friends)):
        if int(friends[idx][1]):
            friends[idx][1] = 'active'
        else:
            friends[idx][1] = 'inactive'
    return friends


def find_nick(friends, id_):
    friend_nick = None
    for friend in friends:
        if friend[0] == id_:
            friend_nick = friend[2]
            break
    return friend_nick

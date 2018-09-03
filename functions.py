import os

def readFile(file_name):
    data = []

    with open(file_name, 'r') as file:
        for line in file:
            word = line[:-1]
            data.append(word)

    file.close()
    return data

def writeFile(file_name, data):
    with open(file_name, 'w') as file:
        for item in data:
            file.write('%s\n' % item)

    file.close()
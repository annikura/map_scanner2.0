def numerize(filename):
    file = open(filename)
    data = file.readlines()
    print(data[0])
    file.close()
    file = open(filename, "w")
    for i in range(len(data)):
        file.write(str(i) + '-' + data[i])
    file.close()

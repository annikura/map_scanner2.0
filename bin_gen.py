file = open("binstr.txt", "wb")
for i in range(256):
    file.write(bytes([i]))
file.close()
file = open("binstr.txt", "rb")
for i in file.read():
    print(i)
file.close()

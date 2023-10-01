i = 0
if i == 1:
    print("1")
    if False:
        print("1.1")
elif i == 2:
    print("2")
    if True:
        print("2.1")
    print("2.2")
else:
    print("3")
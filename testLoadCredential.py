from pip._vendor.distlib.compat import raw_input

input = raw_input('login? ')
#login_info = input.split(" ");


with open('./credentials.txt', "r+") as file:
    for data in file:
        data = data.rstrip()
        if input== data:
            print("work")





def main():
    userName = input('Enter your full name:')
    userAge = '101'
    str = '0123456789'
    while (int(userAge)<=0 or int(userAge)>=100):
        userAge = input('Enter your age as an integer between 1 and 99:')
        for i in userAge:
            if i not in str:
                print('That was not an integer, try again...')
                userAge = '101'
    intUserAge = int(userAge)
    print('Your age is:', intUserAge)
main()
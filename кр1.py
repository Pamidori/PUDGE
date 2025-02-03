def dekorator (uskor):
    def obertka(v1,v2,t):
        a=uskor(v1,v2,t)
        print(v1*t+a*t*t/2)
        print(uskor(v1,v2,t))
    return obertka
try:
    @dekorator
    def uskor(v1,v2,t):
        a=(v2-v1)/t
        return(a)
except ZeroDivisionError:
    print("Нельзя делить на ноль")
except ValueError:
    print("Нельзя вводить строки")

uskor(3,4,5)

f=open('perepis.txt','r')
sum=0
x=int(input('с какого года'))
y=int(input('до какого года'))

for i in f:
    L=i.split()
    print(L[0])
    a=(L[3][-4:])
    a=int(a)
    if a<1978:
        sum+=1
    if x<a and a<y:
        print(L)
print(sum)
#day of week from given date
day=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
a=input()
b=int(input())
i1=day.index(a)
week=(i1+(b-1))%7
print(day[week])

#Total hand shakes for given number of students
N = int(input())
uniqu = N * (N - 1) // 2
print(uniqu)
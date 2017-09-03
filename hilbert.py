import math
import sys
from copy import copy

class Matrix():
    def __init__(self, row1 = None, row2 = None, row3 = None):
        if row3 is None:
            self.arr = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        else:
            self.arr = [row1, row2, row3]

    def __mul__(self, other):
        if type(other) is Matrix:
            result = Matrix()
            for i in range(3):
                for j in range(3):
                    sum = 0
                    for k in range(3):
                        sum += self.arr[i][k] * other.arr[k][j]
                    result.arr[i][j] = sum
            return result
        elif type(other) is Vector:
            result = Vector()
            for i in range(3):
                sum = 0
                for k in range(3):
                    sum += self.arr[i][k] * other.arr[k]	
                result.arr[i] = sum
            return result
        elif type(other) is float or type(other) is int:
            result = Matrix()
            for i in range(3):
                for j in range(3):
                    result.arr[i][j] = self.arr[i][j] * other
            return result
            
    def id(self):
        return Matrix([1, 0, 0], [0, 1, 0], [0, 0, 1])

    def cos(self, x):
        return math.cos(math.radians(x))

    def sin(self, x):
        return math.sin(math.radians(x))
        
    #obrót wokół osi X
    def RX(self, x):
        x = -x
        return Matrix(
        [1, 0, 0],
        [0, self.cos(x), -self.sin(x)],
        [0, self.sin(x), self.cos(x)])
    
    #obrót wokół osi Y
    def RY(self, x):
        x = -x
        return Matrix(
        [self.cos(x), 0, self.sin(x)],
        [0, 1, 0],
        [-self.sin(x), 0, self.cos(x)])
    
    #obrót wokół osi Z
    def RZ(self, x):
        x = -x
        return Matrix(
        [self.cos(x), -self.sin(x), 0],
        [self.sin(x), self.cos(x), 0],
        [0, 0, 1])
        
class Vector():
    def __init__(self, x = None, y = None, z = None):
        if z is None:
            self.arr = [0, 0, 0]
        else:
            self.arr = [x, y, z]
    
    def __add__(self, other):
        return Vector(self.arr[0] + other.arr[0],
        self.arr[1] + other.arr[1],
        self.arr[2] + other.arr[2])
    
    def __sub__(self, other):
        return Vector(self.arr[0] - other.arr[0],
        self.arr[1] - other.arr[1],
        self.arr[2] - other.arr[2])
    
    def __mul__(self, other):
        return Vector(self.arr[0] * other,
        self.arr[1] * other,
        self.arr[2] * other)    
        
#zamień małe liczby na liście wektorów na zera
def make_zeros(arr):
    for i in range(len(arr)):
        for j in range(3):
            eps = 1e-5
            if abs(arr[i].arr[j]) < eps:
                arr[i].arr[j] = 0.0
             
def translate(arr, vector):
    for i in range(len(arr)):
        arr[i] += vector

def multiply(arr, matrix):
    for i in range(len(arr)):
        arr[i] = matrix * arr[i]

#hilbert(stopien, punkt od ktorego startuje rysowanie, macierz obrotu)
def hilbert(n, start, rotation):
    answer = []
    if n is 0:
        answer = [start]
        return answer
    
    point = copy(start)
    
    #1
    list1 = hilbert(n - 1, point, Matrix().RY(-90) * Matrix().RX(-90))
    point = copy(list1[-1])
    point += Vector(0, -1, 0)
    
    #2
    list2 = hilbert(n - 1, point, Matrix().RY(90) * Matrix().RZ(-90))
    point = copy(list2[-1])
    point += Vector(-1, 0, 0)
    
    #3
    list3 = hilbert(n - 1, point, Matrix().RY(90) * Matrix().RZ(-90))
    point = copy(list3[-1])
    point += Vector(0, 1, 0)
    
    #4
    list4 = hilbert(n - 1, point, Matrix().RZ(-90) * Matrix().RZ(-90))
    point = copy(list4[-1])
    point += Vector(0, 0, 1)
    
    #5
    list5 = hilbert(n - 1, point, Matrix().RZ(-90) * Matrix().RZ(-90))
    point = copy(list5[-1])
    point += Vector(0, -1, 0)
    
    #6
    list6 = hilbert(n - 1, point, Matrix().RX(-90) * Matrix().RY(-90))
    point = copy(list6[-1])
    point += Vector(1, 0, 0)
    
    #7
    list7 = hilbert(n - 1, point, Matrix().RX(-90) * Matrix().RY(-90))
    point = copy(list7[-1])
    point += Vector(0, 1, 0)
    
    #8
    list8 = hilbert(n - 1, point, Matrix().RX(90) * Matrix().RZ(90))

    answer = list1 + list2 + list3 + list4 + list5 + list6 + list7 + list8
    
    multiply(answer, rotation)
    #przesuwam wszystkie punkty by pierwszy był w punkcie start
    translate(answer, start - answer[0])
    
    return answer    

#wczytywanie
n = int(sys.argv[1]) #rząd krzywej
s = int(sys.argv[2]) #rozmiar obrazka w pt
u = int(sys.argv[3]) #długość krawędzi sześcianu w pt
d = float(sys.argv[4]) #odległość obserwatora od płaszczyzny rzutu
x = float(sys.argv[5]) #współrzędne początku układu współrzędnych obiektu w pt
y = float(sys.argv[6])
z = float(sys.argv[7])
fi = float(sys.argv[8]) #kąty obrotu
psi = float(sys.argv[9])

#obliczam krzywą bez obrotów zaczanając w początku układu współrzędnych
array = hilbert(n, Vector(0, 0, 0), Matrix().id())

#przesuwam krzywą tak by jej środek był w początku układu współrzędnych
half = (2**n - 1)/2
translate(array, Vector(half, half, -half))

#skaluję krzywą by zajmowała około u jednostek w pliku postscript
multiply(array, Matrix().id() * (u / (2.5 * half)))  

#obracam krzywą według wejścia programu
multiply(array, Matrix().RY(-psi) * Matrix().RX(fi))

#liczę średnią arytmetyczną punktów krzywej (jej środek)
#i przesuwam krzywą tak, by ten środek znalazł się w zadanym punkcie (x, y, z)
mean = Vector()
for vec in array:
    mean += vec
mean = Vector(mean.arr[0] / len(array),
	mean.arr[1] / len(array),
	mean.arr[2] / len(array))

translate(array, Vector(x, y, z) - mean)

#tablica answer to tablica zrzutowanych na płaszczyznę punktów
answer = [Vector(d * vec.arr[0] / (d + vec.arr[2]),
	d * vec.arr[1] / (d + vec.arr[2]), 0.0)
	for vec in array]

#liczę minimum po x-ach i y-kach już zrzutowanych punktów
#by nie było punktów o współrzędnych ujemnych
minx, miny = 1e10, 1e10
for vec in answer:
    if vec.arr[0] < minx:
        minx = vec.arr[0]
    if vec.arr[1] < miny:
        miny = vec.arr[1]

if minx > 0:
    minx = 0
if miny > 0:
    miny = 0

#przesuwam wszystkie punkty o minima oraz o (s - u)/2 by
#krzywa była w miarę na środku
translate(answer, Vector(-minx + (s - u)/2, -miny + (s - u)/2, 0))

make_zeros(answer)  

print("%!PS-Adobe-2.0 EPSF-2.0")
print("%%BoundingBox: 0 0 ", end = '')
print("{} {}".format(s, s))
print("newpath")
for ind, vec in enumerate(answer):          
        print("{:.2f} {:.2f} ".format(vec.arr[0], vec.arr[1]), end = "")
        if ind is 0:
            print("moveto")
        else:
            print("lineto")
print(".02 setlinewidth")
print("stroke")
print("showpage")
print("%%Trailer")
print("%EOF")

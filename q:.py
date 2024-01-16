class a:
 x=1

 def a(self):
    print(self.x)

 def b(self,y):
    x=2
    y=y+1
    def f(g):
      print(f"g:{g}")
      print(f"y:{y}")
      print(f"SELF {self.x}")
    print(x)    
    print(y)
    f(y)

c=a()
c.a()
d=5
c.b(d)

print(d)
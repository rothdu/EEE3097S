import matplotlib.pyplot as plt

# Sample x and y values
x = []
y = []
time = 0

f = open("Main/test/results/realtimecat.csv","r")    
g = f.readlines()

fileLen = len(g)

for i in range(0,fileLen,1):
    g[i] = g[i].strip()

for a in g:
    line = a.split(",")
    time += float(line[4])
    x.append(float(line[2]))
    y.append(float(line[3]))

print(time/len(g))

# Plotting the x and y values
plt.scatter(x, y, marker='o')  # 'o' for circles at data points
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Plot of X and Y values')
plt.xlim(0, 0.8)  # Limit x-axis from 0 to 6
plt.ylim(0, 0.5)  # Limit y-axis from 0 to 25
plt.grid(True)  # Add gridlines for better visibility
plt.show()
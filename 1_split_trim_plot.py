import csv
import math
import plotly as py
import plotly.graph_objs as go
import pandas as pd

# Split sorted files into smaller files with no more than 10000 lines each
lines_per_file = 10000
newfile = None
file_num = 0
my_files = []

with open('Travel_Map_Sorted.csv') as infile:
    for lineno, line in enumerate(infile, -1):
        if lineno >= 0:
            if lineno % lines_per_file == 0:
                if newfile:
                    newfile.close()
                file_num = lineno // lines_per_file + 1
                new_filename = 'datasets/Travel_Map_p{}.csv'.format(file_num)
                my_files.append(new_filename)
                newfile = open(new_filename, 'w')
            newfile.write(line)
    if newfile:
        newfile.close()

print(file_num)
#print(my_files)

#Trim points by density(distance between two closest points)
countOrig = 0
count = 0
coordinates = []

for filename in my_files:
    coords = []
    with open(filename) as infile:
        for row in infile:
            row = row.strip().split(',')
            new_point = (float(row[0]),float(row[1]))

            add = True
            if coords == None:
                coords.append(new_point)
                count += 1
                print(count, 'added:', new_point)
            else:
                for j in range(len(coords) - 1, -1, -1):
                    lat1 = new_point[0]
                    lat0 = coords[j][0]
                    lng1 = new_point[1]
                    lng0 = coords[j][1]

                    deglen = 110.25
                    x = lat1 - lat0
                    yy = lng1 - lng0
                    if x < 0.01 and x > -0.01 and yy < 0.05 and yy > -0.05:
                        y = (yy) * math.cos(lat0)
                        if deglen * math.sqrt(x*x + y*y) < 0.5:
                            add = False
                            break
                if add:
                    coords.append(new_point)
                    count += 1

            countOrig += 1
            if countOrig % 10000 == 0:
                print('Processed:', countOrig)
                print('Added:', count, new_point)

    coordinates = coordinates + coords

print('Points processed:', countOrig)
print('Points addedd:', count)

#Add trimed points to a new file
with open('Travel_Map_Trimmed.csv', mode='w') as outfile:
    outfile.write('Latitude,Longitude\n')
    for pairs in coordinates:
        outfile.write(f'{pairs[0]},{pairs[1]}\n')

#Plot points on an interactive map
mapbox_access_token = 'pk.eyJ1IjoianVub3hkIiwiYSI6ImNqeHR4OWE2ZTAyMHIzbXF2bzR4OTB1bGYifQ.QuzCmekFjzCj5tAVAAJFnA'

source = pd.read_csv('Travel_Map_Trimmed.csv')
latitude = source.Latitude
longitude = source.Longitude

data = [
    go.Scattermapbox(
        lat = latitude,
        lon = longitude,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
    )
]
layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=go.layout.Mapbox(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=25,
            lon=140
        ),
        pitch=0,
        zoom=1.2
    ),
)

fig = go.Figure(data=data, layout=layout)
py.offline.plot(fig, filename='Travel_Map_All.html')

#benchmarking
#python3 -m cProfile -o prof.dat 1_split_trim_plot.py
#python3 -m pstats prof.dat

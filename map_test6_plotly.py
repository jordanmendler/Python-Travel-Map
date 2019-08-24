import plotly as py
import plotly.graph_objs as go

import pandas as pd

mapbox_access_token = 'pk.eyJ1IjoianVub3hkIiwiYSI6ImNqeHR4OWE2ZTAyMHIzbXF2bzR4OTB1bGYifQ.QuzCmekFjzCj5tAVAAJFnA'

source = pd.read_csv('TravelMapAll_trimmed.csv')
latitude = source.Latitude
longitude = source.Longitude
#latitude = latitude[0:70000]
#longitude = longitude[0:70000]

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
            #lat=35.6870,
            #lon=-105.9378
            lat=25,
            lon=140
        ),
        pitch=0,
        zoom=1.2
    ),
)

fig = go.Figure(data=data, layout=layout)
py.offline.plot(fig, filename='Travel Map All')

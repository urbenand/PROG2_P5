import plotly.graph_objects as go
from maybe_usefull_stuff import get_coordinates
import pydoc


class Map:
    def __init__(self, cities):
        fig = go.Figure(go.Scattermapbox(
            mode="markers+lines",
            lon=self.get_coord_list(cities, "lon"),
            lat=self.get_coord_list(cities, "lat"),
            marker={'size': 20}
        ))

        fig.update_layout(
            margin={'l': 0, 't': 0, 'r': 0, 'b': 0},
            mapbox={
                'center': self.get_center(cities),
                'style': "open-street-map",
                'zoom': 10,
                'layers': [{
                    'source': {
                        'type': "FeatureCollection",
                        'features': [{
                            'type': "Feature",
                            'geometry': {
                                'type': "MultiPolygon",
                                'coordinates': [[[
                                    [47.3927146, 8.0444448], [47.3029125, 7.8826232],
                                    [46.9484742, 7.4521749]
                                ]]]
                            }
                        }]
                    },
                    'type': "fill", 'below': "traces", 'color': "royalblue", 'opacity': 0.25}]
            }
        )

        fig.show()

    def get_coord_list(self, cities, type):
        # Type must be either lon or lat
        coord_list = []

        for city in cities:
            coord_list.append(city[type])

        return coord_list

    def get_center(self, cities):
        print(cities[0]["lon"])
        print(cities[0]["lat"])
        print(cities[1]["lon"])
        print(cities[1]["lat"])

        if cities[0]["lon"] > cities[1]["lon"]:
            lon_diff = abs(float(cities[0]["lon"]) - float(cities[1]["lon"])) / 2
        else:
            lon_diff = abs(float(cities[0]["lon"]) + float(cities[1]["lon"])) / 2

        if cities[0]["lat"] > cities[1]["lat"]:
            lat_diff = abs(float(cities[0]["lat"]) - float(cities[1]["lat"])) / 2
        else:
            lat_diff = abs(float(cities[0]["lat"]) + float(cities[1]["lat"])) / 2


        lon_calculated = float(cities[1]["lon"]) - lon_diff
        lat_calculated = float(cities[0]["lat"]) - lat_diff

        center = {'lon': lon_calculated, 'lat': lat_calculated}

        return center


def main():
    # Format for cities:
    # { 'City': {'lat': 47.546, 'lon': 7.59} }

    # Example data
    '''    cities = [{
            'lat': 47.39121,
            'lon': 8.05185
        },
            {
                'lat': 47.37365,
                'lon': 8.2349
            }
        ]'''

    cities = []

    city = ["Zürich", "Winterthur"]

    for cit in city:
        lat, lon = get_coordinates(cit)
        cities.append({'lat': lat, 'lon': lon})

    Map(cities)


if __name__ == '__main__':
    main()
    pydoc.writedoc('my_module')

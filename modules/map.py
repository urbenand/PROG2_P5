# modules/map.py

import plotly.graph_objects as go
import math
from helper import get_coordinates, calculate_triangle_points


class Map:
    def __init__(self, cities):
        print(cities[0])
        coord_A = cities[0]
        coord_B = cities[1]

        # Berechne die nördlichen und südlichen Punkte des Dreiecks
        coord_N, coord_S = calculate_triangle_points(coord_A[0], coord_A[1], coord_B[0], coord_B[1], 10)

        # Create map
        fig = go.Figure()

        # Add triangles for cone
        fig.add_trace(go.Scattermapbox(
            lat=[coord_A[0], coord_N[0], coord_B[0], coord_A[0]],
            lon=[coord_A[1], coord_N[1], coord_B[1], coord_A[1]],
            mode='lines+markers',
            fill='toself',
            fillcolor='rgba(0, 0, 0, 0.5)',
            line=dict(width=2, color='black'),
        ))

        fig.add_trace(go.Scattermapbox(
            lat=[coord_A[0], coord_S[0], coord_B[0], coord_A[0]],
            lon=[coord_A[1], coord_S[1], coord_B[1], coord_A[1]],
            mode='lines+markers',
            fill='toself',
            fillcolor='rgba(0, 0, 0, 0.5)',
            line=dict(width=2, color='black'),
        ))

        # Add departure and destination coordinates as a trace
        fig.add_trace(go.Scattermapbox(
            lon=[coord_A[0], coord_B[0]],
            lat=[coord_A[1], coord_B[1]],
            mode='markers+lines',
            marker=dict(size=20, color=['blue', 'red']),
        ))

        # Kartenlayout einstellen
        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox=dict(
                style='open-street-map',
                center=dict(lat=(coord_A[0] + coord_B[0]) / 2, lon=(coord_A[1] + coord_B[1]) / 2),
                zoom=6
            ),
        )

        fig.show()


def main():
    cities = []

    city = ["Genf", "Romanshorn"]

    for cit in city:
        lat, lon = get_coordinates(cit)
        cities.append((float(lat), float(lon)))

    Map(cities)


if __name__ == '__main__':
    main()

import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import osmnx as ox 
import sklearn
from shapely.geometry import LineString,Point
from shapely.geometry import Polygon
import geopy.distance
import networkx as nx
import folium
import time
from networkx.algorithms.simple_paths import shortest_simple_paths
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from folium.plugins import HeatMap
from pathlib import Path

#df =pd.read_csv('/Users/vmarian/Downloads/2024_accidents_vehicles_gu_bcn.csv') 
pd1= Path(__file__).parent.parent / "datasets" / "2024_1.csv"
df = pd.read_csv(pd1)
e = len(df)
londata = df.Longitud_WGS84
latdata = df.Latitud_WGS84
exceldata = latdata,londata
location_data = None
location1 = None
lat1 = lon1 = None
st.title("geolocation radar map ")
st.subheader(f"Welcome to the Map Page {st.user.name}!")
st.write(f"You are logged in as {st.session_state.role}.")
st.write("select a map type from the dropdown below:")
types_of_maps = [" ","OpenStreetMap", "Esri.WorldImagery", "Hybrid", "Terrain"]
selected_map = st.selectbox("Select a map type:", types_of_maps)
if selected_map == " ":
    st.write("Please select a map type from the dropdown.")
else:
    st.write(f"You selected: {selected_map}, press the button below to get your location and show it on the map.")
geolocator = Nominatim(user_agent="Finder")
geolocator1 = Nominatim(user_agent="Finder1")
geocode1 = RateLimiter(geolocator.reverse, min_delay_seconds=1)  
gtcode = RateLimiter(geolocator1.geocode, min_delay_seconds=1)
from_where = st.selectbox("Select your starting point:", [" ","Current Location", "Custom Location"])
if from_where == "Custom Location":
            st.write("Please use the search box below to enter your custom starting location.")
            st1 = st.text_input("Enter your custom starting location (e.g., 'Sitges'):")
if from_where == "Current Location":
            location = streamlit_geolocation()
        #location(outputs: {'latitude': 35.9700706, 
        #'longitude': -83.9184362, 'altitude': None, 'accuracy': 12.684, 'altitudeAccuracy': None, 'heading': None, 'speed': None})        
if from_where == " ":
            st.write("It is needed to select from the selectbox above and allow location access.")
            st.stop()
with st.form("Where to go?"):
    goto_location = st.text_input("Enter a location to go to (e.g., 'Castelldefels, BCN'):")
    submit = st.form_submit_button("Send location to map")
    if submit:
        if from_where == "Custom Location":
            startlocation = gtcode(st1)
            stlon = startlocation.longitude
            stlat = startlocation.latitude
            location_data = (stlat, stlon)
            location1 = geocode1(f"{stlat}, {stlon}")
        if from_where == "Current Location":
            location_data = location['latitude'], location['longitude']
            location1 = geocode1(f"{location['latitude']}, {location['longitude']}")
        lon1 = location_data[1]
        lat1 = location_data[0]
        st.write("Processing your request...")
        barra = st.progress(0)
        for i in range(99):
                barra.progress(i + 1)
                time.sleep(0.001)
        if goto_location:
            location2 = gtcode(goto_location)
            st.write("DEBUG search string1:", repr(location2))
            if location2 is not None:
                lon2, lat2 = location2.longitude, location2.latitude
                st.write(f"Destination location: {lon2, lat2}")
            else:
                st.error("Could not find the specified location.")
                lon2, lat2 = None, None
        else:
            st.write("Please enter a valid location to go to.")
        if not location_data == (None, None):
            #st.write(f"Your current location is: {location_data}")
            map = leafmap.Map(center=location_data, zoom=18)
            map.add_marker(location_data, popup=f"You are: {location1}" ,draggable=True)
            map.add_marker((lat2, lon2), popup=f" {goto_location}" ,draggable=True)
            #map.add_marker(destination_data, popup=f" {goto_location}" ,draggable=True)
            #origin = (location['latitude'], location['longitude'])
            #destin = (lat2, lon2)
            #dist_m = geopy.distance.distance(origin, destin).meters + 500
            margin = 0.01

            north = max(lat1, lat2) + margin
            south = min(lat1, lat2) - margin
            east  = max(lon1, lon2) + margin
            west  = min(lon1, lon2) - margin

            bbox_polygon = Polygon([
            (west, south),
            (west, north),
            (east, north),
            (east, south),
            (west, south)
                ])
            c = 0
        # Generar grafo de calles dentro del polígono
            G = ox.graph_from_polygon(bbox_polygon, network_type="drive")
            orig = ox.nearest_nodes(G,lon1, lat1)
            dest = ox.nearest_nodes(G, lon2, lat2)
            route = ox.shortest_path(G, orig, dest, weight="length")
            paths = list(ox.k_shortest_paths(G, orig, dest,k=3, weight="length"))
            r1 = ox.shortest_path(G, orig, dest, weight="length")
            G_copy = G.copy()

        #   Add default speeds if missing
            G_copy = ox.add_edge_speeds(G_copy, hwy_speeds=None)   
            G_copy = ox.add_edge_travel_times(G_copy)

        # Now you can safely compute shortest travel_time path
            r2 = ox.shortest_path(G_copy, orig, dest, weight="travel_time")
            distance1 = nx.path_weight(G, r1, weight="length")
            distance2 = nx.path_weight(G_copy, r2, weight="length")
        #time1 = nx.path_weight(G, r1, weight="travel_time")
        #time2 = nx.path_weight(G_copy, r2, weight="travel_time")
            st.markdown(f"<span style='color:blue'>Route 1: Distance = {distance1/1000:.2f} km</span>",
                unsafe_allow_html=True)#, Estimated Time = {time1/60:.2f} minutes")
            st.markdown(f"<span style='color:red'>Route 2: Distance = {distance2/1000:.2f} km</span>",
                unsafe_allow_html=True)
            paths = [r1,r2]
            route_coords = []
            for i, path in enumerate(paths[:2]):
                route_coords.append(path)
            nodes = {f"route_{i+1}": route for i, route in enumerate(route_coords)}         
            with st.container():
                st.markdown("""
                        <div style="text-align:center;">
                        <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTIzcGR1N3pia3kyb3U3cTc4YmtrZjZlaHljNDlsd2I5bWJjOWl5eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/d2jjuAZzDSVLZ5kI/giphy.gif"
                        style="width:120px; margin-bottom:10px;" />
                        </div>
                        """, unsafe_allow_html=True)
        #line = LineString(route_coords)
            map.add_basemap(selected_map)
            colors = ["blue", "red"]
            tolerance = 0.0015
            accidents_in_view = df[
            latdata.between(south - 0.01, north + 0.01) & 
            londata.between(west - 0.01, east + 0.01)
            ]
            route_accidents = []
            #st.write(nodes)
            for i, route in enumerate(route_coords):
            
                route_latlon = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
                route_line = LineString([(lon, lat) for lat, lon in route_latlon])
                #map.add_marker(exceldata ,draggable=True)
            
                for idx, row in accidents_in_view.iterrows():
                    accident_point = Point(row['Longitud_WGS84'], row['Latitud_WGS84'])

                    if route_line.distance(accident_point) < tolerance:
                        route_accidents.append([
                            row['Latitud_WGS84'],
                            row['Longitud_WGS84'],
                        1  # weight (can be severity if you have it)
                        ])
                folium.PolyLine(route_latlon, color=colors[i], weight=5, opacity=0.7).add_to(map)

            if route_accidents:   
                            # Pintamos un círculo ROJO en el mapa (simulando tu heatmap puntual)
                            HeatMap(
                                route_accidents,
                                radius=18,
                                color="red",
                                blur=15,
                                min_opacity=0.4,
                            ).add_to(map)
            if len(route_accidents) > 0:
                st.write(f"Atención: Se han detectado {len(route_accidents)} accidentes históricos DIRECTAMENTE sobre tu ruta.")
            else:
                st.write("La ruta parece limpia de accidentes históricos registrados.")
                
                    
            #route_write = st.write({f"route_{i+1}":route_latlon})
            
            map.to_streamlit(height=600)
            barra.progress(100)
            cz = 100
            if cz > 0:
                st.success("Route successfully calculated and displayed on the map!")
    else:
        st.write("Click the button to send the location to the map.")

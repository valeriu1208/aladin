import streamlit as st
import leafmap.foliumap as leafmap
from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import osmnx as ox 
import sklearn
from shapely.geometry import LineString
from shapely.geometry import Polygon
import geopy.distance
import networkx as nx
import folium
import time

st.title("geolocation radar map ")
st.subheader(f"Welcome to the Map Page {st.user.name}!")
st.write(f"You are logged in as {st.session_state.role}.")
st.write("select a map type from the dropdown below:")
types_of_maps = [" ","OpenStreetMap", "Esri.WorldImagery", "Hybrid", "Terrain"]
selected_map = st.selectbox("Select a map type:", types_of_maps)
if selected_map is selected_map == " ":
    st.write("Please select a map type from the dropdown.")
else:
    st.write(f"You selected: {selected_map}, press the button below to get your location and show it on the map.")
location = streamlit_geolocation() #location(outputs: {'latitude': 35.9700706, 
 #'longitude': -83.9184362, 'altitude': None, 'accuracy': 12.684, 'altitudeAccuracy': None, 'heading': None, 'speed': None})
if location is None:
    st.write("Button wasn't clicked, waiting... and Please ensure that location services are enabled in your browser.")
    st.stop()
location_data = location['latitude'], location['longitude']
geolocator = Nominatim(user_agent="Finder")
geolocator1 = Nominatim(user_agent="Finder1")
geocode1 = RateLimiter(geolocator.reverse, min_delay_seconds=1)  
gtcode = RateLimiter(geolocator1.geocode, min_delay_seconds=1)
location1 = geocode1(f"{location['latitude']}, {location['longitude']}")

lon1 = location_data[1]
lat1 = location_data[0]
if st.form("Where to go?"):
    goto_location = st.text_input("Enter a location to go to (e.g., 'Castelldefels, BCN'):")
    if st.button("Send location to map"):
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
            st.write(f"Your current location is: {location_data}")
            map = leafmap.Map(center=location_data, zoom=18)
            map.add_marker(location_data, popup=f"You are: {location1}" ,draggable=True)
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
            route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]
            with st.container():
                st.markdown("""
                        <div style="text-align:center;">
                        <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExMTIzcGR1N3pia3kyb3U3cTc4YmtrZjZlaHljNDlsd2I5bWJjOWl5eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/d2jjuAZzDSVLZ5kI/giphy.gif"
                        style="width:120px; margin-bottom:10px;" />
                        </div>
                        """, unsafe_allow_html=True)
            barra = st.progress(0)
            for i in range(100):
                barra.progress(i + 1)
                time.sleep(0.001)
            line = LineString(route_coords)
            map.add_basemap(selected_map)
            folium.PolyLine(route_coords, color="blue", weight=5).add_to(map)
            map.to_streamlit(height=600)
            cz = 100
            if cz > 0:
                st.success("Route successfully calculated and displayed on the map!")
    else:
        st.write("Click the button to send the location to the map.")
else:
    st.error("Please enter a location to go to.")

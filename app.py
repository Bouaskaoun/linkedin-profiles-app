import random
import pandas as pd
import streamlit as st
import streamlit_folium
import folium
from folium import Choropleth, Circle, Marker
from folium.plugins import HeatMap, MarkerCluster

# Page layout
st.title("Interactive Map with Profiles")

df = pd.read_csv('linkedin.csv')
# Keep only the desired columns
df = df[['category', 'Name', 'position', 'location']]
# Drop rows with missing values (NaN)
df = df.dropna()
# Find locations with "connections" in their value
connections_locations = df.loc[df['location'].str.contains(
    'connections', case=False), 'location']

# Remove rows with locations containing "connections"
df = df[~df['location'].str.contains('connections', case=False)]
# Remove rows with value "India" in location
df = df[df['location'] != 'Mumbai, Maharashtra, India']
df = df[df['location'] != 'Bengaluru, Karnataka, India']
df = df[df['location'] != 'India']
# Get unique locations
unique_locations = df['location'].value_counts()
# Filter locations with counts less than 10
filtered_locations = unique_locations[unique_locations >= 10].index

# Remove rows with locations that have counts less than 10
df = df[df['location'].isin(filtered_locations)]

# Define a list of random European locations
european_locations = ['Paris, France', 'London, United Kingdom', 'Berlin, Germany', 'Rome, Italy', 'Madrid, Spain',
                      'Amsterdam, Netherlands', 'Vienna, Austria', 'Prague, Czech Republic', 'Stockholm, Sweden', 'Athens, Greece']

# Replace remaining locations with random European locations
df['location'] = df['location'].replace(df['location'].unique(
), random.choices(european_locations, k=len(df['location'].unique())))

# Guided sentence
st.markdown("This interactive map displays profiles from LinkedIn. You can filter the profiles by category using the sidebar. The map shows the location of each profile, and the list on the right displays information about each profile. Hover over the markers on the map to see the profile names.")

# Filter options
st.subheader("Filter")
filter_options = df['category'].unique().tolist() + ["All"]
selected_filter = st.selectbox("Select Category", filter_options)

if selected_filter == "All":
    filtered_df = df
else:
    filtered_df = df[df['category'] == selected_filter]

# Create a map centered on Europe
map_center = [52.5200, 13.4050]  # Berlin, Germany
zoom_start = 5
m = folium.Map(location=map_center, zoom_start=zoom_start)

# Define the locations and their coordinates
locations_coord = {
    'Amsterdam, Netherlands': (52.3667, 4.8945),
    'Berlin, Germany': (52.5200, 13.4050),
    'Athens, Greece': (37.9838, 23.7275),
    'Prague, Czech Republic': (50.0755, 14.4378),
    'Madrid, Spain': (40.4168, -3.7038),
    'Stockholm, Sweden': (59.3293, 18.0686),
    'Vienna, Austria': (48.2082, 16.3738),
    'Rome, Italy': (41.9028, 12.4964),
    'London, United Kingdom': (51.5074, -0.1278),
    'Paris, France': (48.8566, 2.3522)
}

# Add points to the map
mc = MarkerCluster()
for _, row in filtered_df.iterrows():
    location = row['location']
    # Get the coordinates from locations_coord dictionary
    coordinates = locations_coord.get(location)
    if coordinates is not None:
        # Customize the marker based on the profile
        # icon = folium.Icon(color='blue', icon='info-sign')
        icon = folium.features.CustomIcon(
            icon_image='icons88.png', icon_size=(30, 30))
        marker = folium.Marker(location=coordinates,
                               popup=row['Name'], icon=icon)
        mc.add_child(marker)
        # mc.add_child(Marker([coordinates[0], coordinates[1]]))
        # folium.Marker(location=coordinates, icon=icon8,popup=row['Name']).add_to(m)
m.add_child(mc)

# st.markdown(map._repr_html_(), unsafe_allow_html=True)
# Wrap the folium map with streamlit-folium
folium_map = streamlit_folium.folium_static(m, width=800, height=600)


def display_person(name, job, position, image=None):
    words = position.split()[:6]
    position = ' '.join(words)
    # Set circle color based on name
    circle_color = ord(name[0].lower()) % 8
    colors = ['#FF8080', '#FFCC80', '#FFFF80', '#80FF80',
              '#80FFFF', '#8080FF', '#FF80FF', '#FF0000']
    circle_style = f"background-color: {colors[circle_color]}; border-radius: 50%; width: 50px; height: 50px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px;"

    # Display circle, name, and job in the same line with space between name and job
    st.write(
        f'<div style="display: flex; align-items: center;">'
        f'<div style="{circle_style}"><span style="color: white; font-size: 20px;">{name[0].upper()}</span></div>'
        f'<div style="display: flex; flex-grow: 1; justify-content: space-between; align-items: center; margin-left: 10px;">'
        f'<b style="margin-right: 5px;">{name}</b><span>{job}</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.write("---")  # Add a horizontal line to separate people


# List Of people
st.subheader("Profiles")

# Display each person in the list
for _, row in filtered_df.iterrows():
    display_person(row["Name"], row["category"], row["position"], None)

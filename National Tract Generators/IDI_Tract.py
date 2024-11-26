import requests
import geopandas as gpd
import csv
from shapely.geometry import mapping
from collections import defaultdict
import os
import pandas as pd
# Function to fetch intersections using Overpass API
def fetch_intersections_overpass(polygon, year):
    """
    Fetches intersections using Overpass API, including implicit intersections where multiple ways share nodes.
    """
    polygon = gpd.GeoSeries([polygon], crs="EPSG:3857").to_crs(epsg=4326).iloc[0]
    minx, miny, maxx, maxy = polygon.bounds
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:60][date:"{year}-01-01T00:00:00Z"];
    (
      node[highway]({miny},{minx},{maxy},{maxx});
      way[highway]({miny},{minx},{maxy},{maxx});
    );
    out body;
    >;
    out skel qt;
    """
    response = requests.get(overpass_url, params={'data': query})
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return 0

    data = response.json().get('elements', [])
    node_degree = defaultdict(int)

    for element in data:
        if element['type'] == 'way' and 'nodes' in element:
            for node_id in element['nodes']:
                node_degree[node_id] += 1  # Track node usage across ways

    # Count intersections: nodes with degree > 1
    intersection_count = sum(1 for count in node_degree.values() if count > 1)
    return intersection_count
# Function to calculate IDI for a given GeoJSON input, year, and output prefix
def calculate_idi(input_geojson, output_prefix, year, aggregate_file):
    data = gpd.read_file(input_geojson)
    data = data.to_crs(epsg=3857)  # Project to EPSG:3857 for area calculations
    areas = data.geometry.area
    geoids = data["GEOID"] if "GEOID" in data.columns else data["geoid"]

    intersection_counts = []
    for idx, polygon in enumerate(data.geometry):
        print(f"Processing polygon {idx + 1}/{len(data.geometry)} for year {year}...")
        intersection_count = fetch_intersections_overpass(polygon, year)
        intersection_counts.append(intersection_count)

    # Calculate intersection density
    intersection_density = [count / area if area > 0 else 0 for count, area in zip(intersection_counts, areas)]

    # Normalize IDI
    max_density = max(intersection_density) if intersection_density else 1
    idi = [density / max_density for density in intersection_density]

    # Add fields to GeoDataFrame
    data["Intersection Count"] = intersection_counts
    data["Polygon Area"] = areas
    data["Intersection Density"] = intersection_density
    data["IDI"] = [0] * len(data)  # Placeholder for IDI
    data["Coordinates"] = data.geometry.apply(lambda geom: mapping(geom)["coordinates"])
    data['Polygon Area'] = data.geometry.area

    # Convert back to EPSG:4326 for output
    data = data.to_crs(epsg=4326)
    
    columns_to_keep = ["GEOID", "Intersection Count", "Intersection Density", "IDI", "Polygon Area", "Coordinates", "geometry"]
    data = data[columns_to_keep]
    
    geoidandyear = data["GEOID"] + "+" + str(year)
    # Append to aggregate file
    aggregate_df = pd.DataFrame({
        "GEOID": geoidandyear,
        "Intersection Density": data["Intersection Density"]
    })
    if os.path.exists(aggregate_file):
        aggregate_df.to_csv(aggregate_file, mode='a', header=False, index=False)
    else:
        aggregate_df.to_csv(aggregate_file, mode='w', header=True, index=False)

    # Save outputs as GeoJSON and CSV
    geojson_file = f"{output_prefix}_{year}_IDI.geojson"
    csv_file = f"{output_prefix}_{year}_IDI.csv"
    data.to_file(geojson_file, driver="GeoJSON")
    data.drop(columns="geometry").to_csv(csv_file, index=False)

    print(f"Processed {year}. Outputs saved to '{geojson_file}' and '{csv_file}'.")
# Census Tracts
calculate_idi(
    input_geojson="part_1.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year="2013",
    aggregate_file="IDI_tract_all.csv"
)
calculate_idi(
    input_geojson="part_2.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year="2013",
    aggregate_file="IDI_tract_all.csv"
)
calculate_idi(
    input_geojson="part_3.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year="2013",
    aggregate_file="IDI_tract_all.csv"
)
calculate_idi(
    input_geojson="part_4.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year="2013",
    aggregate_file="IDI_tract_all.csv"
)
calculate_idi(
    input_geojson="part_1.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year="2017",
    aggregate_file="IDI_tract_all.csv"
)
calculate_idi(
    input_geojson="tracts_lower.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year="2022",
    aggregate_file="IDI_tract_all.csv"
)
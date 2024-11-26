import requests
import geopandas as gpd
import csv
from shapely.geometry import mapping, Point
from collections import defaultdict
import os
import pandas as pd
import numpy as np
def fetch_commercial_data(polygon, year):
    """
    Fetches commercial data using Overpass API for a given polygon and year.
    Args:
        polygon (shapely.geometry.Polygon): Polygon representing the geographic area.
        year (int): Year for which data is being fetched.
    Returns:
        list: A list of shapely Point objects representing commercial points of interest.
    """
    # Transform the polygon to EPSG:4326
    polygon = gpd.GeoSeries([polygon], crs="EPSG:3857").to_crs(epsg=4326).iloc[0]
    minx, miny, maxx, maxy = polygon.bounds
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json][timeout:60][date:"{year}-01-01T00:00:00Z"];
    (
      node["shop"]({miny},{minx},{maxy},{maxx});
      node["amenity"~"restaurant|cafe|bank|school|cinema"]({miny},{minx},{maxy},{maxx});
      node["leisure"~"park|sports_centre|stadium"]({miny},{minx},{maxy},{maxx});
    );
    out body;
    """
    
    response = requests.get(overpass_url, params={'data': query})
    if response.status_code != 200:
        print(f"Error fetching data from Overpass API: {response.status_code}")
        return []
    
    elements = response.json().get('elements', [])
    return [
        Point(element['lon'], element['lat'])
        for element in elements if 'lat' in element and 'lon' in element
    ]
def calculate_cdi(input_geojson, output_prefix, year, aggregate_file):
    """
    Calculates Commercial Density Index (CDI) for a given GeoJSON input file, year, and outputs the results.
    Args:
        input_geojson (str): Path to the input GeoJSON file containing tract polygons.
        output_prefix (str): Prefix for output files.
        year (int): Year for which CDI is calculated.
        aggregate_file (str): File path to append aggregate results.
    """
    # Load GeoJSON data
    data = gpd.read_file(input_geojson).to_crs(epsg=3857)
    
    # Prepare storage for commercial counts and densities
    commercial_counts = []
    commercial_densities = []
    
    # Process each polygon
    print(f"Processing year {year}...")
    all_poi_points = []
    for idx, polygon in enumerate(data["geometry"]):
        print(f"  Fetching commercial data for polygon {idx + 1}/{len(data)}...")
        try:
            poi_points = fetch_commercial_data(polygon, year)
            all_poi_points.extend(poi_points)
        except Exception as e:
            print(f"  Error processing polygon {idx + 1}: {e}")
    
    # Create a GeoDataFrame of all points of interest
    all_poi_gdf = gpd.GeoDataFrame(geometry=all_poi_points, crs="EPSG:4326").to_crs(epsg=3857)
    
    # Perform spatial join to count POIs within each polygon
    joined = gpd.sjoin(all_poi_gdf, data, how="inner", predicate="within")
    counts = joined.groupby(joined.index_right).size().reindex(data.index, fill_value=0)
    
    # Calculate densities
    densities = counts.values / data.geometry.area
    max_density = densities.max() if densities.max() > 0 else 1
    cdi = densities / max_density
    
    # Add results to the GeoDataFrame
    data["Commercial Count"] = counts.values
    data['Polygon Area'] = data.geometry.area
    data["Commercial Density"] = densities
    data["Coordinates"] = data.geometry.apply(lambda geom: mapping(geom)["coordinates"])
    data["CDI"] = cdi
    
    columns_to_keep = ["GEOID", "Commercial Count", "Commercial Density", "CDI", "Polygon Area", "Coordinates", "geometry"]
    data = data[columns_to_keep]
    
    # Save results to GeoJSON and CSV
    geojson_output = f"{output_prefix}_{year}_CDI.geojson"
    csv_output = f"{output_prefix}_{year}_CDI.csv"
    data.to_crs(epsg=4326).to_file(geojson_output, driver="GeoJSON")
    data.drop(columns=["geometry"]).to_csv(csv_output, index=False)
    
    # Append aggregate results
    geoidandyear = data["GEOID"] + "+" + str(year)
    aggregate_df = pd.DataFrame({
        "GEOID": geoidandyear,
        "Commercial Density": densities,
    })
    if os.path.exists(aggregate_file):
        aggregate_df.to_csv(aggregate_file, mode="a", header=False, index=False)
    else:
        aggregate_df.to_csv(aggregate_file, mode="w", header=True, index=False)
    
    print(f"Results saved to {geojson_output} and {csv_output}.")
# Census Tracts
calculate_cdi(
    input_geojson="tracts.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year=2013,
    aggregate_file="CDI_tract_all.csv"
)
calculate_cdi(
    input_geojson="tracts.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year=2017,
    aggregate_file="CDI_tract_all.csv"
)
calculate_cdi(
    input_geojson="tracts.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year=2022,
    aggregate_file="CDI_tract_all.csv"
)

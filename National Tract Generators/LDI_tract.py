import geopandas as gpd
import requests
import csv
import numpy as np
from shapely.geometry import Polygon, LineString, mapping
import os
import pandas as pd
# Define a function to fetch data from Overpass API for a polygon and a specific year
def fetch_landuse_data(polygon, year):
    print(f"fetching for year {year}")
    polygon = gpd.GeoSeries([polygon], crs="EPSG:3857").to_crs(epsg=4326).iloc[0]
    bounds = polygon.bounds  # (minx, miny, maxx, maxy)
    bbox = f"{bounds[1]},{bounds[0]},{bounds[3]},{bounds[2]}"
    query = f"""
    [out:json][date:"{year}-01-01T00:00:00Z"];
    (
      way["landuse"]({bbox});
      relation["landuse"]({bbox});
    );
    out geom;
    """
    try:
        response = requests.get("http://overpass-api.de/api/interpreter", params={'data': query}, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Overpass API request failed: {e}")
        return None
# Function to calculate LDI for a given GeoJSON input, year, and output prefix
def calculate_ldi(input_geojson, output_prefix, year, aggregate_file):
    # Load GeoJSON data
    data = gpd.read_file(input_geojson)

    # Initialize storage for entropy and land use dictionaries
    entropies = []
    landuse_dictionaries = []

    # Reproject to EPSG:3857 for area calculations
    data = data.to_crs(epsg=3857)

    for idx, polygon in enumerate(data.geometry):
        try:
            # Fetch land use data
            landuse_data = fetch_landuse_data(polygon, year)
            if not landuse_data or 'elements' not in landuse_data:
                entropies.append(0)
                landuse_dictionaries.append({})
                continue

            # Process geometries and land use types
            geometries = []
            landuse_types = []
            for element in landuse_data['elements']:
                if 'geometry' in element:
                    coords = [(pt['lon'], pt['lat']) for pt in element['geometry']]
                    if len(coords) < 3:
                        geometries.append(LineString(coords))
                    else:
                        geometries.append(Polygon(coords))
                    landuse_types.append(element['tags'].get('landuse', ''))

            # Create GeoDataFrame for land use types
            gdf = gpd.GeoDataFrame({'landuse': landuse_types, 'geometry': geometries}, crs="EPSG:4326").to_crs(epsg=3857)
            gdf["area"] = gdf.geometry.area

            # Aggregate area by land use type
            landuse_area_dict = gdf.groupby('landuse')['area'].sum().to_dict()
            landuse_dictionaries.append(landuse_area_dict)

            # Filter and calculate entropy
            valid_landuse_dict = {k: v for k, v in landuse_area_dict.items() if v > 0}
            total_area = sum(valid_landuse_dict.values())
            k = len(valid_landuse_dict)

            if k > 1 and total_area > 0:
                denominator = np.log(k)
                numerator = -sum((v / total_area) * np.log(v / total_area) for v in valid_landuse_dict.values())
                entropies.append(numerator / denominator)
            else:
                entropies.append(0)
        except Exception as e:
            print(f"Error processing polygon {idx + 1}: {e}")
            entropies.append(0)
            landuse_dictionaries.append({})

    # Calculate LDI
    max_entropy = max(entropies) if entropies else 0
    ldis = [e / max_entropy if max_entropy else 0 for e in entropies]

    # Add fields to GeoDataFrame
    data["Entropy"] = entropies
    data["LDI"] = [0] * len(data)  # Placeholder field for 'LDI'
    data["Coordinates"] = data.geometry.apply(lambda geom: mapping(geom)["coordinates"])
    data['Polygon Area'] = data.geometry.area

    # Convert back to EPSG:4326 for output
    data = data.to_crs(epsg=4326)

    columns_to_keep = ["GEOID", "Entropy", "LDI", "Polygon Area", "Coordinates", "geometry"]
    data = data[columns_to_keep]
    
    geoidandyear = data["GEOID"] + "+" + str(year)
    # Append to aggregate file
    aggregate_df = pd.DataFrame({
        "GEOID": geoidandyear,
        "Entropy": data["Entropy"]
    })
    if os.path.exists(aggregate_file):
        aggregate_df.to_csv(aggregate_file, mode='a', header=False, index=False)
    else:
        aggregate_df.to_csv(aggregate_file, mode='w', header=True, index=False)

    # Save outputs as GeoJSON and CSV
    geojson_file = f"{output_prefix}_{year}_LDI.geojson"
    csv_file = f"{output_prefix}_{year}_LDI.csv"
    data.to_file(geojson_file, driver="GeoJSON")
    data.drop(columns="geometry").to_csv(csv_file, index=False)

    print(f"Processed {year}. Outputs saved to '{geojson_file}' and '{csv_file}'.")
# Census Tracts
calculate_ldi(
    input_geojson="tracts.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year=2013,
    aggregate_file="LDI_tract_all.csv"
)
calculate_ldi(
    input_geojson="tracts.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year=2017,
    aggregate_file="LDI_tract_all.csv"
)
calculate_ldi(
    input_geojson="tracts.geojson",  # Replace with your census tract GeoJSON file
    output_prefix="tracts",
    year=2022,
    aggregate_file="LDI_tract_all.csv"
)
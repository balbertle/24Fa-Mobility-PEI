# Pedestrian Environment Index (PEI) Implementation

This project implements the Pedestrian Environment Index (PEI) methodology as developed at the University of Illinois Chicago (see the research paper: [https://www.sciencedirect.com/science/article/pii/S0966692314001343](https://www.sciencedirect.com/science/article/pii/S0966692314001343)). The PEI provides a composite measure of the walkability of an environment, incorporating the following subindices:

* Population Density Index (PDI)
* Commercial Density Index (CDI)
* Intersection Density Index (IDI)
* Land-use Diversity Index (LDI)

## Team

| Name                  | Seniority | Major                  | Department | GitHub Handle                                                 | 
| --------------------- | --------- | ---------------------- | ---------- | ------------------------------------------------------------- | 
| C. "Albert" Le        | Sophomore | Computer Engineering   | ECE        | [balbertle](https://github.com/balbertle)                     | 
| Chunlan Wang          | Masters   | Architecture (DC)      | ARCH       | [wang-123-xi](https://github.com/wang-123-xi)                 | 
| Yichao Shi            | PhD       | Architecture           | ARCH       | [SHIyichao98](https://github.com/SHIyichao98)                 | 
| Atharva Beesen        | Junior    | Computer Science       | COC        | [AtharvaBeesen](https://github.com/AtharvaBeesen)             | 



**Motivation**

Understanding the walkability of an environment is important for urban planning, public health initiatives, and promoting active transportation. This implementation of the PEI can be used by researchers to:

* Assess the current walkability of neighborhoods or regions
* Compare walkability across different areas
* Identify areas with potential for improvement

**Getting Started**



* **Prerequisites:**
   * Python 3.x 
   * **Libraries:**
        * osmnx
        * pandas
        * numpy
        * matplotlib.pyplot
        * csv
        * census
   * Census API Key: Can be found at: [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html). **Must paste key in text file titled census_api_key.txt in the same directory as PDI_generator.ipynb to access population data.**

**Installation**

You can install the required libraries using pip:

```bash
pip install osmnx pandas numpy matplotlib csv census
```
## Pedestrian Environment Index (PEI) Documentation
The Pedestrian Environment Index (PEI) is a composite measure of walkability that combines four key subindices to evaluate pedestrian-friendly environments.

## Core Subindices

### Population Density Index (PDI)

  Measures residential population density within defined areas

  Data sourced from Census block groups

### Commercial Density Index (CDI)

  Evaluates density of commercial establishments per Block Group

  Indicates availability of walkable destinations and services

### Intersection Density Index (IDI)

  Quantifies intersection density within an area

  Evaluates route options and pedestrian safety

### Land-use Diversity Index (LDI)

  Analyzes mix of land-use types (residential, commercial, industrial)

  Assesses environment walkability through land use diversity

## Methodology

### PDI Documentation

  Method of calculation

  Population and area data downloaded from the Missouri Census Data Center

  https://mcdc.missouri.edu/cgi-bin/uexplore?/data

  *Area is land area 

  Population density  = Total population / Total Area (Square Miles) 

  PDI = Population density / (max population density - min population density) * 100 (Already normalized)

### CDI Documentation

  Method of calculation

  Overpass API is used to retrieve the total amount of commercial points of interest. The following is the full list of tags used, but can be expanded upon in the future:

  - All shops
  - Restaurants
  - Cafes
  - Banks
  - Schools
  - Cinemas
  - Parks
  - Sports centers
  - Stadiums
  	
  Area is from census tracts from the US Census geojson
  	
  Commercial Density = count of commercial POIs / total land area (Square Miles)
  
  CDI = Commercial Density / (Max Commercial Density)

### IDI Documentation
  
  Method of calculation
  
  Overpass API is used to retrieve the amount of intersections and nodes connected to it within the polygon area. 
   
  Area is from census tracts from the US Census geojson
  	
  Intersection Density = Number of nodes that are part of more than one way (intersections) / Area (Square Miles)
  
  IDI = Intersection Density / (Max Intersection Density)

### LDI Documentation
  
  Method of calculation
  
   Overpass API is used to retrieve the land use of an area. This is done by fetching data tagged with “landuse”. For documentation on what all is included in “landuse”, refer to OSMNX: https://wiki.openstreetmap.org/wiki/Key:landuse.
  
  The area of each type of land use is summed. 
  	
  Entropy is how diverse the land use types are within the polygon. 
  
  Entropy = Summation(Area of land use type/Total area*ln(Area of land use type/Total area)) for all land use types with non-zero area
  
  Normalized by dividing by ln(number of land use types with non-zero area).

## Implementation Workflow

1. Files
  - Download population data files from MCDC for each year needed
  - Download block group and census tract files from US Census Bureau website
2. Subindex calculation
  - Individual generator Python scripts process shapefiles
  - Each generator produces the subindex value
  - Outputs CSV and GeoJSON files
3. Normalization 
  - Normalize the data with the max value being 100 and the min value being 0
  - Outputs into CSV files for each subindex
4. PEI Calculation
  - Run normalized data into PEI generator
  - Outputs CSV and GeoJSON
5. Web App
  -  Upload to AWS buckets for implementation and visualization on the web app 
  - Use Leaflet to visualize

 
![Alt text](imagesFolder/2013peiatl.png?raw=true "2013")
2013
![Alt text](imagesFolder/2022peiatl.png?raw=true "2022")
2022


## Usage
1. Retrieve API key if using Census API for PDI
2. Else, download year requested for CSV from https://mcdc.missouri.edu/cgi-bin/uexplore?/data
3. Change names and paths in the generator scripts to desired files


**Contributing**



**License**

Idk how licensing works... Just don't sell it I guess.

***

# Presentation

<a href="https://youtu.be/Eqtjx-CYxUg?si=MhWMFuBX-LoGsxPb" target="_blank" rel="noopener noreferrer">
    <img src="https://img.youtube.com/vi/Eqtjx-CYxUg/maxresdefault.jpg" width="480" alt="Final Presentation --- 24Fa - Pedestrian Environment Index (PEI)">
</a>

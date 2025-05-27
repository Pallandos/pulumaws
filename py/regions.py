"""
This file loads the regions settings
"""

import yaml

def load_regions_config(file_path: str) -> dict:
    """
    Load regions configuration from a YAML file.

    Args:
        file_path (str): Path to the YAML file containing regions configuration.

    Returns:
        dict: A dictionary containing the regions configuration.
    """
    try:
        with open(file_path, 'r') as file:
            regions_config = yaml.safe_load(file)
            return regions_config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")
    
def load_clean_regions_config(file_path: str) -> dict:
    """
    Load regions configuration and filter out regions with 0 instances.
    
    Args:
        file_path (str): Path to the YAML file containing regions configuration.
    
    Returns:
        dict: A cleaned dictionary containing only regions with instances > 0.
    """
    full_config = load_regions_config(file_path) 
    cleaned_regions = {}
    
    for continent_name, continent_data in full_config['continents'].items():
        
        for region_name, region_config in continent_data['region'].items():
            if region_config['instances'] > 0:
                cleaned_regions[region_name] = region_config
    
    
    return cleaned_regions

def get_region_names(file_path: str) -> list:
    """
    Get a list of region names from the CLEANED regions configuration file.

    Args:
        file_path (str): Path to the YAML file containing regions configuration.

    Returns:
        list: A list of region names.
        
    Example:
        >>> get_region_names("regions.yaml")
        {'us-east-1': {'instances': 1}, 'eu-west-1': {'instances': 1}}
    """
    regions_config = load_clean_regions_config(file_path)
    region_names = []
    for region in regions_config.keys():
        region_names.append(region)
    return region_names

if __name__ == "__main__":
    # example usage
    regions_path = "regions.yaml"  # Replace with your actual path

    cleaned_regions = load_clean_regions_config(regions_path)
    print("Cleaned Regions Configuration:")
    print(cleaned_regions)
    
    region_names = get_region_names(regions_path)
    print("Region Names:")
    print(region_names)
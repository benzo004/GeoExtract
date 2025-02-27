#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import webbrowser
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import PyPDF2
import pyfiglet
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

def print_banner():
    """Print ASCII art banner for GeoExtract"""
    # Utiliser une police compatible mais impressionnante
    try:
        banner = pyfiglet.figlet_format("GeoExtract", font="slant")
    except:
        # Fallback si la police n'est pas disponible
        print(f"{Fore.RED}Warning: Font not found, using default font.{Style.RESET_ALL}")
        banner = pyfiglet.figlet_format("GeoExtract", font="standard")
    
    # Ajouter un cadre autour du texte pour le mettre en évidence
    lines = banner.split('\n')
    # Filtrer les lignes vides à la fin
    while lines and not lines[-1].strip():
        lines.pop()
    
    width = max(len(line) for line in lines)
    border = f"{Fore.RED}{'=' * (width + 4)}{Style.RESET_ALL}"
    
    print(border)
    for line in lines:
        print(f"{Fore.RED}| {Fore.WHITE}{line.ljust(width)}{Fore.RED} |{Style.RESET_ALL}")
    print(border)
    
    print(f"{Fore.YELLOW}A tool to extract geolocation data from images and PDFs{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Created by: benzo004 {Style.RESET_ALL}")
    print(f"{Fore.RED}{'=' * (width + 4)}{Style.RESET_ALL}\n")

def convert_to_degrees(value):
    """Helper function to convert GPS coordinates to degrees"""
    try:
        # Pour les objets IFDRational
        if hasattr(value[0], 'numerator') and hasattr(value[0], 'denominator'):
            degrees = float(value[0].numerator) / float(value[0].denominator)
            minutes = float(value[1].numerator) / float(value[1].denominator) / 60.0
            seconds = float(value[2].numerator) / float(value[2].denominator) / 3600.0
        # Pour les tuples (numerator, denominator)
        else:
            degrees = float(value[0][0]) / float(value[0][1])
            minutes = float(value[1][0]) / float(value[1][1]) / 60.0
            seconds = float(value[2][0]) / float(value[2][1]) / 3600.0
        
        return degrees + minutes + seconds
    except Exception as e:
        print(f"Error converting GPS coordinates: {e}")
        # Fallback simple method
        try:
            return float(value[0]) + float(value[1])/60 + float(value[2])/3600
        except:
            return 0

def get_gps_from_exif(exif_data):
    """Extract GPS info from EXIF data"""
    if not exif_data:
        return None
    
    gps_info = {}
    
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == "GPSInfo":
            for gps_tag, gps_value in value.items():
                gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                gps_info[gps_tag_name] = gps_value
    
    if not gps_info:
        return None
    
    gps_latitude = gps_info.get('GPSLatitude')
    gps_latitude_ref = gps_info.get('GPSLatitudeRef')
    gps_longitude = gps_info.get('GPSLongitude')
    gps_longitude_ref = gps_info.get('GPSLongitudeRef')
    
    if not all([gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref]):
        return None
    
    lat = convert_to_degrees(gps_latitude)
    if gps_latitude_ref != "N":
        lat = -lat
    
    lon = convert_to_degrees(gps_longitude)
    if gps_longitude_ref != "E":
        lon = -lon
    
    return lat, lon

def extract_from_image(image_path):
    """Extract geolocation data from an image file"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            print(f"{Fore.YELLOW}No EXIF data found in the image.{Style.RESET_ALL}")
            return None
        
        # Convert EXIF data to a more readable format
        exif_readable = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            exif_readable[tag_name] = value
        
        # Extract GPS coordinates
        gps_coords = get_gps_from_exif(exif_data)
        
        # Print all EXIF data
        print(f"{Fore.CYAN}EXIF Metadata:{Style.RESET_ALL}")
        for tag, value in exif_readable.items():
            if tag != "GPSInfo":  # We'll handle GPS info separately
                print(f"{Fore.WHITE}{tag}: {value}{Style.RESET_ALL}")
        
        return gps_coords
    
    except Exception as e:
        print(f"{Fore.RED}Error processing image: {e}{Style.RESET_ALL}")
        return None

def extract_from_pdf(pdf_path):
    """Extract geolocation data from a PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = pdf_reader.metadata
            
            if not metadata:
                print(f"{Fore.YELLOW}No metadata found in the PDF.{Style.RESET_ALL}")
                return None
            
            print(f"{Fore.CYAN}PDF Metadata:{Style.RESET_ALL}")
            for key, value in metadata.items():
                print(f"{Fore.WHITE}{key}: {value}{Style.RESET_ALL}")
            
            # Look for GPS coordinates in the metadata
            # This is a simplified approach; actual implementation might need more parsing
            for key, value in metadata.items():
                if isinstance(value, str) and ('GPS' in key or 'geo' in key.lower()):
                    print(f"{Fore.GREEN}Potential GPS data found in metadata: {key}: {value}{Style.RESET_ALL}")
            
            # Parse through the text of the PDF to look for coordinates
            coords = None
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # This is a very basic pattern matching and would need to be improved
                # for a production application
                if "GPS" in text or "coordinates" in text.lower():
                    print(f"{Fore.YELLOW}Page {page_num + 1} contains potential GPS references.{Style.RESET_ALL}")
            
            return coords
    
    except Exception as e:
        print(f"{Fore.RED}Error processing PDF: {e}{Style.RESET_ALL}")
        return None

def open_coordinates_in_browser(latitude, longitude):
    """Open the coordinates in a web browser using OpenStreetMap with a red marker"""
    zoom_level = 15  # Zoom level between 1 (world view) and 19 (detailed view)
    
    # OpenStreetMap affiche déjà un marqueur rouge par défaut avec le paramètre mlat/mlon
    url = f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}&zoom={zoom_level}"
    
    print(f"{Fore.GREEN}Opening coordinates in browser: {url}{Style.RESET_ALL}")
    webbrowser.open(url)

def create_test_image_with_gps():
    """Create a test image with GPS metadata for testing purposes"""
    try:
        # Vérifier si piexif est installé
        import piexif
    except ImportError:
        print(f"{Fore.RED}Error: piexif module not found. Installing it now...{Style.RESET_ALL}")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "piexif"])
        import piexif
    
    print(f"{Fore.CYAN}Creating a test image with GPS metadata...{Style.RESET_ALL}")
    
    # Create a simple image
    img = Image.new('RGB', (100, 100), color = 'red')
    
    # GPS coordinates for the Eiffel Tower in Paris
    # Convert to rational values as required by piexif
    lat_deg = (48, 1)  # 48 degrees
    lat_min = (51, 1)  # 51 minutes
    lat_sec = (30, 1)  # 30 seconds (approx)
    
    lon_deg = (2, 1)   # 2 degrees
    lon_min = (17, 1)  # 17 minutes
    lon_sec = (40, 1)  # 40 seconds (approx)
    
    # Prepare EXIF data with GPS information
    zeroth_ifd = {
        piexif.ImageIFD.Make: "GeoExtract Test",
        piexif.ImageIFD.Model: "Test Camera",
        piexif.ImageIFD.Software: "GeoExtract Test Script"
    }
    
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: "N",
        piexif.GPSIFD.GPSLatitude: [lat_deg, lat_min, lat_sec],
        piexif.GPSIFD.GPSLongitudeRef: "E",
        piexif.GPSIFD.GPSLongitude: [lon_deg, lon_min, lon_sec],
        piexif.GPSIFD.GPSAltitudeRef: 0,
        piexif.GPSIFD.GPSAltitude: (330, 1)  # Altitude in meters
    }
    
    exif_dict = {
        "0th": zeroth_ifd,
        "GPS": gps_ifd
    }
    
    exif_bytes = piexif.dump(exif_dict)
    
    # Save the image with EXIF data
    output_path = "test_image_with_gps.jpg"
    img.save(output_path, "jpeg", exif=exif_bytes)
    
    print(f"{Fore.GREEN}Test image created: {output_path}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}GPS coordinates embedded: 48 deg 51' 30\" N, 2 deg 17' 40\" E (Eiffel Tower, Paris){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Now you can test GeoExtract with this command:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}python geoextract.py {output_path}{Style.RESET_ALL}")

def main():
    """Main function to parse arguments and execute the program"""
    parser = argparse.ArgumentParser(description='Extract geolocation data from images and PDFs')
    parser.add_argument('file', nargs='?', help='Path to the image or PDF file')
    parser.add_argument('--no-browser', action='store_true', help='Do not open coordinates in browser')
    parser.add_argument('--manual-coords', nargs=2, metavar=('LAT', 'LON'), help='Manually specify coordinates (latitude longitude)')
    parser.add_argument('--create-test', action='store_true', help='Create a test image with GPS metadata')
    
    args = parser.parse_args()
    
    # Print the banner
    print_banner()
    
    # Check if user wants to create a test image
    if args.create_test:
        create_test_image_with_gps()
        return
    
    # Check if manual coordinates are provided
    if args.manual_coords:
        try:
            latitude = float(args.manual_coords[0])
            longitude = float(args.manual_coords[1])
            print(f"\n{Fore.GREEN}Using manually provided coordinates:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Latitude: {latitude}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Longitude: {longitude}{Style.RESET_ALL}")
            
            if not args.no_browser:
                open_coordinates_in_browser(latitude, longitude)
            
            return
        except ValueError:
            print(f"{Fore.RED}Error: Invalid coordinates format. Please provide valid numbers.{Style.RESET_ALL}")
            sys.exit(1)
    
    # If no manual coordinates or test image creation, we need a file
    if not args.file:
        print(f"{Fore.RED}Error: Either a file, manual coordinates, or --create-test must be provided.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Usage examples:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}python geoextract.py image.jpg{Style.RESET_ALL}")
        print(f"{Fore.WHITE}python geoextract.py --manual-coords 48.858333 2.294444{Style.RESET_ALL}")
        print(f"{Fore.WHITE}python geoextract.py --create-test{Style.RESET_ALL}")
        sys.exit(1)
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"{Fore.RED}Error: File '{args.file}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)
    
    # Process the file based on its extension
    file_extension = os.path.splitext(args.file)[1].lower()
    
    if file_extension in ['.jpg', '.jpeg', '.png', '.tiff', '.webp']:
        print(f"{Fore.CYAN}Processing image file: {args.file}{Style.RESET_ALL}")
        coords = extract_from_image(args.file)
    elif file_extension == '.pdf':
        print(f"{Fore.CYAN}Processing PDF file: {args.file}{Style.RESET_ALL}")
        coords = extract_from_pdf(args.file)
    else:
        print(f"{Fore.RED}Unsupported file type: {file_extension}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Display coordinates and open in browser if found
    if coords:
        latitude, longitude = coords
        print(f"\n{Fore.GREEN}GPS Coordinates found:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Latitude: {latitude}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Longitude: {longitude}{Style.RESET_ALL}")
        
        if not args.no_browser:
            open_coordinates_in_browser(latitude, longitude)
    else:
        print(f"\n{Fore.YELLOW}No GPS coordinates found in the file.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You can manually specify coordinates using the --manual-coords option:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}python geoextract.py --manual-coords LATITUDE LONGITUDE{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

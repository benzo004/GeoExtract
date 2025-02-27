# GeoExtract 🔎📍

A powerful command-line tool for extracting geolocation metadata from images and PDF files.

## Key Features
- Extracts GPS coordinates from EXIF metadata in various image formats (JPG, PNG, TIFF, WebP).
- Processes PDF files to find embedded location data.
- Displays extracted coordinates with a marker on OpenStreetMap.
- Cross-platform compatibility (Windows and Linux).
- Simple interface with helpful command-line options.
- Built-in test image creation for easy demonstration.
- Option to manually input coordinates for visualization.

## Use Cases
- Digital forensics and metadata analysis.
- Photography organization and mapping.
- Educational purposes for understanding embedded metadata.
- Location data extraction and visualization.

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/benzo004/GeoExtract.git
   cd GeoExtract
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Basic usage:
```sh
python geoextract.py path/to/your/file.jpg
```

Options:
```sh
python geoextract.py --help
```

### Examples

Process an image file:
```sh
python geoextract.py photo.jpg
```

Process a PDF file:
```sh
python geoextract.py document.pdf
```

Process a file without opening the browser:
```sh
python geoextract.py photo.jpg --no-browser
```

Manually specify coordinates:
```sh
python geoextract.py --manual-coords 48.858333 2.294444
```

Create a test image with embedded GPS coordinates:
```sh
python geoextract.py --create-test
```

## Supported File Types

- **Images**: JPG, JPEG, PNG, TIFF, WebP
- **Documents**: PDF

## Project Structure

The project is structured as follows:

- **geoextract.py**: Main script with all functionality.
- **requirements.txt**: List of dependencies.
- **README.txt**: Documentation.

## Disclaimer

This tool is for educational purposes only. Always respect privacy and copyright when analyzing files.

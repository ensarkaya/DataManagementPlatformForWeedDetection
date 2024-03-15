from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import exifread
import re


def extract_numeric_value(s):
    # Extract the first numeric value from the string
    match = re.search(r'\d+(\.\d+)?', s)
    return match.group(0) if match else None


def parse_gps_coordinate(coord):
    """
    Parses a GPS coordinate string into degrees, minutes, and seconds.

    :param coord: A string representing the GPS coordinate.
    :return: A tuple of (degrees, minutes, seconds).
    """
    # Extracting numeric values from the string
    nums = re.findall(r'\d+/?\d*', coord)
    degrees, minutes, seconds = 0.0, 0.0, 0.0

    if len(nums) >= 1:
        degrees = float(nums[0])
    if len(nums) >= 2:
        minutes = float(nums[1])
    if len(nums) == 3:
        # Handling fraction for seconds
        seconds = float(nums[2].split('/')[0]) / float(nums[2].split('/')[1]) if '/' in nums[2] else float(nums[2])

    return degrees, minutes, seconds


def convert_gps_to_decimal(gps_coord, gps_ref):
    """
    Converts GPS coordinates from degrees, minutes, and seconds to decimal format.

    :param gps_coord: A string representing degrees, minutes, and seconds.
    :param gps_ref: A string representing the direction ('N', 'S', 'E', 'W').
    :return: Decimal representation of the GPS coordinate.
    """
    if not gps_coord:
        return None

    try:
        degrees, minutes, seconds = parse_gps_coordinate(gps_coord)

        # Converting to decimal
        decimal = degrees + (minutes / 60) + (seconds / 3600)
        if gps_ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except (ValueError, IndexError, TypeError):
        return None


def get_image_metadata(uploaded_file):
    tags = exifread.process_file(uploaded_file, details=False)
    metadata = {
        "gps_latitude_ref": str(tags.get("GPS GPSLatitudeRef", "")),
        "gps_latitude": str(tags.get("GPS GPSLatitude", "")),
        "gps_longitude_ref": str(tags.get("GPS GPSLongitudeRef", "")),
        "gps_longitude": str(tags.get("GPS GPSLongitude", "")),
        "gps_altitude": extract_numeric_value(str(tags.get("GPS GPSAltitude", ""))),
    }
    return metadata


def resize_image(original_image, target_size=(1024, 1024)):
    with Image.open(original_image) as img:
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        return ContentFile(output.read(), name=original_image.name)
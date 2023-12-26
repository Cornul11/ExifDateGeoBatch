import re
from datetime import datetime


def convert_to_decimal(lat, long):
    return (
        lat[0][0] + lat[1][0] / 60 + lat[2][0] / lat[2][1] / 3600,
        long[0][0] + long[1][0] / 60 + long[2][0] / long[2][1] / 3600,
    )


def format_date_for_exif(date_str):
    """Format the date in the EXIF date format."""
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y:%m:%d %H:%M:%S")


def convert_to_degrees(value):
    d, m, s = value
    return d[0] / d[1] + m[0] / m[1] / 60 + s[0] / s[1] / 3600


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def convert_to_rational(value):
    absolute = abs(value)
    degrees = int(absolute)
    minutes = int((absolute - degrees) * 60)
    seconds = (absolute - degrees - minutes / 60) * 3600 * 100
    return (degrees, 1), (minutes, 1), (int(seconds), 100)


def format_gps_for_exif(gps_str):
    lat_str, lon_str = gps_str.split(", ")
    lat = convert_to_rational(float(lat_str))
    lon = convert_to_rational(float(lon_str))

    return {
        "GPSLatitude": lat,
        "GPSLongitude": lon,
        "GPSLatitudeRef": "N" if float(lat_str) >= 0 else "S",
        "GPSLongitudeRef": "E" if float(lon_str) >= 0 else "W",
    }


def is_valid_gps(gps_str):
    gps_pattern = re.compile(r"^-?\d+(\.\d+)?, -?\d+(\.\d+)?$")
    return bool(gps_pattern.match(gps_str))


def format_gps_display(gps_data):
    lat = gps_data.get("Latitude", "No GPS Latitude Data")
    lon = gps_data.get("Longitude", "No GPS Longitude Data")

    return f"Latitude: {lat}, Longitude: {lon}"

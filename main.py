import os
import smtplib

import requests
import datetime as dt

LATITUDE = 49.8955367
LONGITUDE = -97.1384584
LOCAL_UTC_OFFSET = -5
MY_EMAIL = os.environ["EMAIL"]
MY_PASSWORD = os.environ["PASSWORD"]
RECIPIENT_EMAIL = os.environ["RECIPIENT EMAIL"]


def utc_to_local(utc_hour):
    """
    This is a function that takes in a time in UTC, then converts and returns that time in the local time (
    determined by LOCAL_UTC_OFFSET)
    """
    # Change UTC time into local area time
    utc_hour += LOCAL_UTC_OFFSET

    # adjust if time goes over 24 hours or under 0 hours.
    if LOCAL_UTC_OFFSET > 0:
        if utc_hour > 23:
            utc_hour -= 24
    elif LOCAL_UTC_OFFSET < 0:
        if utc_hour < 0:
            utc_hour += 24

    # return resulting time in local area time
    return utc_hour


def is_ISS_near():
    """
    This is a function that returns whether the ISS is within 5 degrees of the person.
    """
    return (abs(iss_location()[0] - LATITUDE) <= 5) and (abs(iss_location()[1] - LONGITUDE) <= 5)


def send_email():
    """
    Sends an email informing recipient that the ISS is near.
    """
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=RECIPIENT_EMAIL,
            msg=f"Subject: The International Space Station is above you in the sky!\n\nGo outside and spot the "
                f"International Space Station. It's currently at Latitude: {iss_location()[0]} and "
                f"Longitude: {iss_location()[1]}. "
        )


def iss_location():
    """
    Returns the latitude and longitude of the ISS as a tuple
    """
    # ISS data
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    # ISS latitude and longitude
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    return (iss_latitude, iss_longitude)


def is_night():
    """
    Returns if currently it is night.
    """
    # Sunrise and sunset data
    parameters = {
        "lat": LATITUDE,
        "lng": LONGITUDE,
        "formatted": 0,
    }
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()

    # Sunrise and sunset data in UTC
    sunrise_utc = int(data["results"]["sunrise"].split('T')[1].split(":")[0])
    sunset_utc = int(data["results"]["sunset"].split('T')[1].split(":")[0])

    # Sunrise and sunset times in local area time
    sunrise = utc_to_local(sunrise_utc)
    sunset = utc_to_local(sunset_utc)

    # Current hour
    time_now = dt.datetime.now().hour

    return time_now >= sunrise or time_now >= sunset


# Send email if ISS is near
if is_ISS_near() and is_night():
    send_email()

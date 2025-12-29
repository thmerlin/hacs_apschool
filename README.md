# APSchool integration for Home Assistant

This integration generates sensor for as many childs that are connected to the account you will log in.

In the sensor, there will be additional attributes with some data in it:

- balance
- number of messages unread


# Development settings

To update the Home Assistant version to use, edit the `requirements.txt` file at the root folder. This version of Home Assistant must exist on [PyPi](https://pypi.org/project/homeassistant/). Once done, rebuild the container.

# Integration Testing

Use "Mockoon" so that it exposes the mock API for APSchool.
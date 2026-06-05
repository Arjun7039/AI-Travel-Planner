from tools.weather import get_weather
from tools.places import search_places

# Test weather
print(get_weather("London"))
print("---")

# Test places
print(search_places("London", "tourist attractions"))
import csv
import random

# Bounds of Kerala
min_lat, max_lat = 8.087, 12.615
min_long, max_long = 74.850, 77.654

# Generate 1000 random data points within the bounds of Kerala
data = []
for i in range(1000):
    lat = round(random.uniform(min_lat, max_lat), 4)
    long = round(random.uniform(min_long, max_long), 4)
    crime_rate = round(random.uniform(0, 10), 2)
    data.append([lat, long, crime_rate])

# Write the data to a CSV file
with open('crime_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['latitude', 'longitude', 'crime_rate'])
    writer.writerows(data)

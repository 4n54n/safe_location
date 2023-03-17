import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import DistanceMetric
import io
import base64
from datetime import timedelta
import mysql.connector

import os
from flask import (
    Flask, session, redirect, url_for,
    render_template, request
)

app = Flask(__name__)
app.secret_key = 'mysecretkey'

app.permanent_session_lifetime = timedelta(hours=1)

# Load the crime data from the CSV file
crime_data = pd.read_csv('crime_data.csv')
BING_MAPS_API_KEY = 'AhETvb0ezYzJJ_GeTfKGSUKRFaZJoFHYD7beSs1n1EZxmU_LqFk1U4vc2rj9Pdhk'



# Function to authenticate username and password
def authenticate(username, password):
    # Here, we are using a local MySQL database to store the credentials
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        database="mydatabase"
    )

    mycursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    val = (username, password)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()

    if result:
        return True
    else:
        return False




@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if session.get('is_logged_in'):
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html')

    elif request.method == 'POST':
        user_name = request.form.get('username')
        passwd = request.form.get('password')

        if authenticate(user_name, passwd):
            session['is_logged_in'] = True
            session.permanent = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', cant_authenticate=True)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'GET':
        if session.get('is_logged_in'):
            return render_template('dashboard.html')
        else:
            return redirect(url_for('login'))

    elif request.method == 'POST':
        if session.get('is_logged_in'):
            file = request.files['file']

            # Save the uploaded file to the root directory
            file.save(os.path.join(app.root_path, 'crime_data.csv'))
            return 'File uploaded successfully'
        else:
            return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    if request.get_json():
        session['is_logged_in'] = False

        # specify in which location you want go after you logout
        resp = {
            "resp": url_for('login')
        }
        return resp


@app.route('/', methods=['GET', 'POST'])
def index():
    # crime_rate = 3.05
    # latitude = 10.516
    # longitude = 76.2157
    crime_rate = 0
    latitude = 0
    longitude = 0

    base64_scatter_plot = open('./static/assets/blank_scatter_plot_base64_str.txt', 'r').read()
    base64_scatter_plot = 'data:image/png;base64,' + base64_scatter_plot

    base64_bar_chart = open('./static/assets/blank_bar_chart_base64_str.txt', 'r').read()
    base64_bar_chart = 'data:image/png;base64,'+ base64_bar_chart

    if request.method == 'POST':
        # Extract the latitude and longitude from the form data
        data = request.get_json()
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))

        # Find the 10 closest locations to the input latitude and longitude
        dist = DistanceMetric.get_metric('haversine')
        distances = dist.pairwise(
            crime_data[['latitude', 'longitude']], [(latitude, longitude)]
        )[:, 0]
        crime_data['distance'] = distances
        closest_locations = crime_data.sort_values('distance').iloc[:10]

        # Train a linear regression model on the closest locations
        model = LinearRegression()
        model.fit(
            pd.DataFrame(closest_locations, columns=['latitude', 'longitude']),
            closest_locations['crime_rate']
        )

        # Predict the crime rate for the input location

        crime_rate = round(model.predict([[latitude, longitude]])[0], 2)
        # Create the scatter plot
        plt.figure(figsize=(8, 6))
        plt.title('Crime Rate in Kerala')
        plt.scatter(crime_data['longitude'], crime_data['latitude'],
                    c=crime_data['crime_rate'], cmap='plasma')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')

        # Add a green marker for the input location with the predicted crime rate
        plt.scatter(
            longitude, latitude, c='green', s=100, label=f'Predicted crime rate: {crime_rate}'
        )
        plt.legend()

        # Save the plot to memory
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Encode the bytes object to Base64
        base64_scatter_plot = base64.b64encode(buf.getvalue()).decode('utf-8')
        base64_scatter_plot = 'data:image/png;base64,' + base64_scatter_plot

        # Create the bar chart
        plt.figure(figsize=(8, 6))
        plt.title('Crime Rate by Location: Nearest 10 Locations')
        bars = plt.bar(
            range(len(closest_locations)), closest_locations['crime_rate'], color='purple'
        )
        plt.xticks(range(len(closest_locations)), closest_locations.index)
        plt.xlabel('Location')
        plt.ylabel('Crime Rate')

        # Add a legend to explicitly show which bar represents your location
        bars[0].set_color('green')
        plt.legend([bars[0]], ['Your location'])

        # Save the plot to memory
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Encode the bytes object to Base64
        base64_bar_chart = base64.b64encode(buf.getvalue()).decode('utf-8')
        base64_bar_chart = 'data:image/png;base64,'+base64_bar_chart

        context = {
            'latitude': latitude, 'longitude': longitude, 'bing_maps_api_key': BING_MAPS_API_KEY
        }
        # Render the results page with the plots
        # return render_template('index.html', crime_rate=crime_rate, **context)
        resp = {
            'result': render_template(
                'index.html', crime_rate=crime_rate, base64_scatter_plot=base64_scatter_plot,
                base64_bar_plot=base64_bar_chart, **context
            )
        }
        return resp

    context = {
        'latitude': latitude, 'longitude': longitude, 'bing_maps_api_key': BING_MAPS_API_KEY
    }
    # If the method is GET, render the input form page
    return render_template(
        'index.html', crime_rate=crime_rate, base64_scatter_plot=base64_scatter_plot,
        base64_bar_plot=base64_bar_chart, **context
    )


if __name__ == '__main__':
    app.run(debug=True)

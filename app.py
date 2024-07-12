from flask import Flask
from flask import request, redirect, url_for, render_template, jsonify
import requests

# debug only
import json

app = Flask(__name__)

# base html index rendering
@app.route("/", methods=["GET", "POST"])
def index():
    # get landing page with GET
    if request.method == "GET":
        return render_template("index.html")
    # if we POST the name, redirect to the city URL handler
    elif request.method == "POST":
        city_name = request.form["cityName"]
        return redirect(url_for("get_weather", city=city_name))

# process POST request on button press
@app.route("/<city>", methods=["GET"])
def get_weather(city):
    print(f"DEBUG {city=}")

    api_url = f"https://v2.wttr.in/{city}?format=j1"

    if city:
        response = requests.get(api_url)
        if response.status_code == 200:
        # === DEBUG ONLY, PROVIDES HARD CODED JSON VALUE ==================
        # if True:
        #     with open("request.json", "r", encoding="UTF8") as txt:
        #         data = json.load(txt)
            data = response.json()

            # parse data
            current_weather_info = {
                "city": data["haha"]["nearest_area"][0]["areaName"][0]["value"],
                "region": data["nearest_area"][0]["region"][0]["value"],
                "country": data["nearest_area"][0]["country"][0]["value"],

                "feels_like_temp": data["current_condition"][0]["FeelsLikeC"],
                "current_temp": data["current_condition"][0]["temp_C"],
                "cloud_cover": data["current_condition"][0]["cloudcover"],
                "humidity": data["current_condition"][0]["humidity"],
                "precip_MM": data["current_condition"][0]["precipMM"],
                "pressure": data["current_condition"][0]["pressure"],
                "uv_index": data["current_condition"][0]["uvIndex"],
                "visibility": data["current_condition"][0]["visibility"],
                "wind_speed": data["current_condition"][0]["windspeedKmph"],
                "wind_direction_16p": data["current_condition"][0]["winddir16Point"],
                "weather_description": data["current_condition"][0]["weatherDesc"][0]["value"],
            }

            # wttr.in returns 4 days of forecast, let's use it
            three_days_forecast = data["weather"]
            forecast_weather_info = {}
            for day in range(len(three_days_forecast)):
                forecast_weather_info[day] = three_days_forecast[day]

            # current day hourly forecast
            current_day_hour_info_curr = forecast_weather_info[0]["hourly"]
            current_day_hour_info = {}
            # change how hours are displayed
            hours_replace = {
                "0": "00:00",
                "300": "03:00",
                "600": "06:00",
                "900": "09:00",
                "1200": "12:00",
                "1500": "15:00",
                "1800": "18:00",
                "2100": "21:00",
            }
            for hour in current_day_hour_info_curr:
                current_day_hour_info[hours_replace[hour["time"]]] = {
                    "WindGustKmph": hour["WindGustKmph"],
                    "chanceofrain": hour["chanceofrain"],
                    "tempC": hour["tempC"],
                    "weatherDesc": hour["weatherDesc"][0]["value"],
                }

            # next 4 days forecast
            next_three_days_forecast = {}
            for day in three_days_forecast:
                next_three_days_forecast[day["date"]] = {
                    "mintempC": day["mintempC"],
                    "avgtempC": day["avgtempC"],
                    "maxtempC": day["maxtempC"],
                }

            return render_template('current_weather.html',
                current_weather_info=current_weather_info,
                hourly_info=current_day_hour_info,
                three_days=next_three_days_forecast
            )
        else:
            return jsonify({"error": "City not found"}), 404
    else:
        return jsonify({"error": "No city provided"}), 400

if __name__ == "__main__":
    app.run(debug=True)

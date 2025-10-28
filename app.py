from flask import Flask, render_template, request, jsonify
import requests
from zeep import Client

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/country-info', methods=['POST'])
def country_info():
    data = request.get_json()
    country_name = data['country']
    target_currency = data['target_currency']

    # SOAP 1 - Country Info
    country_wsdl = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL"
    country_client = Client(country_wsdl)

    try:
        country_info = country_client.service.FullCountryInfo(country_name[:2].upper())
    except Exception:
        return jsonify({'error': 'Invalid country or service unavailable'})

    # Extract main details
    capital = country_info.sCapitalCity
    currency = country_info.sCurrencyISOCode
    continent = country_info.sContinentCode

    # SOAP 2 - Currency Conversion (Simulated for demo)
    # try:
    #     converted_value = f"1 {currency} ≈ simulated {target_currency} rate"
    # except Exception:
    #     converted_value = "Conversion unavailable"
    # SOAP 2 - Currency Conversion (using REST API)
    # REST API - Currency Conversion (robust version)
    try:
        if not currency or len(currency) != 3:
            converted_value = "Invalid or missing currency code"
        else:
            response = requests.get(
                f"https://api.exchangerate.host/convert?from={currency}&to={target_currency}"
            )
            data = response.json()
            print("🔍 Currency API Response:", data)  # debug output
            if 'info' in data and 'rate' in data['info']:
                rate = data['info']['rate']
                converted_value = f"1 {currency} = {rate:.2f} {target_currency}"
            elif 'result' in data:
                rate = data['result']
                converted_value = f"1 {currency} = {rate:.2f} {target_currency}"
            else:
                converted_value = "Conversion unavailable"
    except Exception as e:
        print("❌ Currency Conversion Error:", e)
        converted_value = "Conversion unavailable"



    # SOAP 3 - Temperature service (Demo example)
    try:
        temp_wsdl = "https://www.w3schools.com/xml/tempconvert.asmx?WSDL"
        temp_client = Client(temp_wsdl)
        avg_temp_c = 10.0  # mock data
        avg_temp_f = temp_client.service.CelsiusToFahrenheit(str(avg_temp_c))
    except Exception:
        avg_temp_f = "Unavailable"

    return jsonify({
        'country': country_name,
        'capital': capital,
        'currency': currency,
        'converted_value': converted_value,
        'average_temp': f"{avg_temp_c}°C / {avg_temp_f}°F",
        'continent': continent
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

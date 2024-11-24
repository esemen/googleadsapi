## Google ADS API Python Integration
### Introduction
This program is a simple integration of Google Ads API using Python. It is a simple program that fetches the data from Google Ads API and displays it in a tabular format. The program is written in Python and uses the Google Ads API library to fetch the data. The program is designed to be simple and easy to use, and can be easily modified to suit your needs.

### Requirements
- Python 3.9 or higher
- Google Ads API library
- Google Ads API credentials
- Google Ads API developer token
- Google Ads API client ID
- Google Ads API client secret
- Google Ads API refresh token

## Creating Google Cloud Project
1. Go to the Google Cloud Console: https://console.cloud.google.com/
2. Click on the project drop-down and create a new project.
3. Add adwords API to the project.
4. Configure the OAuth consent screen.
5. Create OAuth 2.0 credentials.
6. Download the credentials file and save it as `credentials.json`.

## Getting Refresh Token (MacOS)
1. Install oauth2l utility using the following command:
```brew install oauth2l```
2. Run the following command to get the refresh token:
```oauth2l fetch --credentials credentials.json --scope adwords --output_format refresh_token```
3. Complete the authentication process and copy the refresh token.

## Setting Up Google Ads API
1. Install the Google Ads API library using the following command:
```pip install google-ads```

## Create YAML File
1. Copy the file from official github repository: https://github.com/googleads/google-ads-python/blob/HEAD/google-ads.yaml
2. Fill the file with the relevant information.
3. Save the file as `google-ads.yaml`.

## Running the Flask App
1. Create a virtual environment using the following command:
```python -m venv venv```
2. Activate the virtual environment using the following command:
```source venv/bin/activate```
3. Install the required libraries using the following command:
```pip install -r requirements.txt```
4. Rename config/google-ads-sample.yaml to config/google-ads.yaml and fill in the relevant information.
5. Run the following command to start the Flask app:
```python app.py```
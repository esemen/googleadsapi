from re import error

from flask import Flask, render_template
from google.ads.googleads.errors import GoogleAdsException
from ads import get_google_client, get_login_customer_id, get_account_details, get_client_list, get_campaign_list

app = Flask(__name__)

import yaml

MANAGER_CUSTOMER_ID = get_login_customer_id()


# Define the home route
@app.route("/")
def index_view():
    # Get the manager account details

    # Load the Google Ads client
    client = get_google_client()
    manager_accounts = get_account_details(client, MANAGER_CUSTOMER_ID)

    # Get the list of child accounts
    all_customers = get_client_list(client=client, customer_id=MANAGER_CUSTOMER_ID, max_level=10, include_manager=True)

    return render_template("index.html",
                           manager_accounts=manager_accounts,
                           customers=all_customers)  # Define the home route


@app.route("/account/<customer_id>")
def client_view(customer_id):
    # Load the Google Ads client
    client = get_google_client()

    customer = get_account_details(client, customer_id)

    try:
        campaigns = get_campaign_list(client, customer_id)
        errors = None
    except GoogleAdsException as e:
        campaigns = []
        errors = e.failure.errors[0].message

    return render_template("client.html",
                           customer=customer,
                           campaigns=campaigns,
                           errors=errors)


# Run the app
if __name__ == "__main__":
    app.run(debug=True)

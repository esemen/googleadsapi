from functools import lru_cache
from os import path
import pandas as pd
import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

ADS_CONFIG_PATH = path.join(path.dirname(path.realpath(__file__)), "config", "google-ads.yaml")


def get_login_customer_id():
    with open(ADS_CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config["login_customer_id"]


def get_google_client():
    # Load the Google Ads client from the configuration file
    return GoogleAdsClient.load_from_storage(ADS_CONFIG_PATH)


def get_account_list(client) -> list:
    # Create a CustomerService client
    customer_service = client.get_service("CustomerService")

    try:
        # Get all accessible customer accounts for the current login_customer_id
        response = customer_service.list_accessible_customers()

        account_ids = []
        for resource_name in response.resource_names:
            # Extract the customer ID from the resource name
            customer_id = resource_name.split("/")[-1]
            account_ids.append(customer_id)

        return account_ids
    except GoogleAdsException as ex:
        print(f"Request failed with error: {ex}")
        for error in ex.failure.errors:
            print(f"Error: {error.message}")


def get_account_details(client, customer_id):
    # Create a GoogleAdsService client
    service = client.get_service("GoogleAdsService")

    try:
        # Query to get account details
        query = """
            SELECT
                customer.id,
                customer.descriptive_name,
                customer.currency_code,
                customer.time_zone
            FROM customer
        """

        # Execute the query
        response = service.search(customer_id=customer_id, query=query)

        account_details = []
        for row in response:
            account_details.append({
                "Customer ID": row.customer.id,
                "Name": row.customer.descriptive_name,
                "Currency": row.customer.currency_code,
                "Time Zone": row.customer.time_zone
            })
        return account_details

    except GoogleAdsException as ex:
        print(f"Request failed with error: {ex}")
        for error in ex.failure.errors:
            print(f"Error: {error.message}")


@lru_cache
def get_client_list(client, customer_id, max_level=1, include_manager=False):
    """Gets the account hierarchy of the given MCC and login customer ID.

    Args:
      client: The Google Ads client.
      customer_id:  Manager account ID.
    """

    # Gets instances of the GoogleAdsService and CustomerService clients.
    googleads_service = client.get_service("GoogleAdsService")

    # Creates a query that retrieves all child accounts of the manager
    # specified in search calls below.
    query = f"""
        SELECT
          customer_client.id,
          customer_client.client_customer,
          customer_client.level,
          customer_client.manager,
          customer_client.descriptive_name,
          customer_client.currency_code,
          customer_client.time_zone
        FROM customer_client
        WHERE customer_client.level <= {max_level}"""

    response = googleads_service.search(customer_id=str(customer_id), query=query)

    # Iterates over all rows in all pages to get all customer
    # clients under the specified customer's hierarchy.

    clients = []
    for googleads_row in response:
        if include_manager or not googleads_row.customer_client.manager:
            customer_client = googleads_row.customer_client
            clients.append({
                "id": customer_client.id,
                "client_customer": customer_client.client_customer,
                "manager": customer_client.manager,
                "resource_name": customer_client.resource_name,
                "descriptive_name": customer_client.descriptive_name,
                "level": customer_client.level,
                "currency_code": customer_client.currency_code,
                "time_zone": customer_client.time_zone
            })

    # query = """
    #     SELECT
    #         customer_client_link.resource_name,
    #         customer_client_link.status,
    #         customer_client_link.client_customer,
    #         customer_client_link.manager_link_id,
    #         customer_client_link.hidden
    #     FROM
    #         customer_client_link
    # """
    #
    # response = googleads_service.search(customer_id=str(customer_id), query=query)
    #
    # client_links = []
    # for row in response:
    #     link = row.customer_client_link
    #     client_links.append({
    #         "client_link.id": link.manager_link_id,
    #         "client_link.client_id": int(link.client_customer.split("/")[-1]),
    #         "client_link.resource_name": link.resource_name,
    #         "client_link.status": link.status.name,
    #         "client_link.hidden": link.hidden
    #     })
    #
    # # Customer Manager Link
    # manager_links = []
    # query = """
    #     SELECT
    #       customer_manager_link.manager_customer,
    #       customer_manager_link.manager_link_id,
    #       customer_manager_link.resource_name,
    #       customer_manager_link.status
    #     FROM customer_manager_link
    # """
    #
    # response = googleads_service.search(customer_id=str(customer_id), query=query)
    #
    # manager_links = []
    # for row in response:
    #     link = row.customer_manager_link
    #     manager_links.append({
    #         "manager_link.id": link.manager_link_id,
    #         "manager_link.manager_id": int(link.manager_customer.split("/")[-1]),
    #         "manager_link.resource_name": link.resource_name,
    #         "manager_link.status": link.status.name
    #     })

    return clients


def get_campaign_list(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")

    query = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      campaign.advertising_channel_sub_type,
      campaign.serving_status,
      campaign.start_date,
      campaign.end_date,
      campaign.network_settings.target_google_search,
      campaign.network_settings.target_search_network,
      campaign.network_settings.target_content_network,
      campaign.network_settings.target_partner_search_network,
      campaign_budget.amount_micros,
      campaign_budget.delivery_method,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.cost_micros
    FROM
      campaign
    ORDER BY
      campaign.id
      """

    # Issues a search request using streaming.
    stream = ga_service.search_stream(customer_id=str(customer_id), query=query)

    campaigns = []

    for batch in stream:
        for row in batch.results:
            # Add all campaign details to the list
            campaigns.append({
                "info": row.campaign,
                "budget": row.campaign_budget,
                "metrics": row.metrics})

    return campaigns

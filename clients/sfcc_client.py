import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import json
import config



##########################################################
# OCAPI AccountAuthentication and Token request functions       #
##########################################################
def OCAPI_Authenticate_OAuth2(instance, authType, sfcc_client_id, sfcc_secret, sfcc_user=None, sfcc_password=None):
    from requests.auth import HTTPBasicAuth

    ###############################################
    # Initializing the response status code texts #
    ###############################################
    API_status_code_texts = {
        "200" : "Everything went okay, and the result has been returned, if any.",
        "301" : "The server is redirecting you to a different endpoint. This can happen when a company switches domain names, or an endpoint name is changed.",
        "400" : "The server thinks you made a bad request. This can happen when you don’t send along the right data, among other things.",
        "401" : "The server thinks you’re not authenticated. Many APIs require login ccredentials, so this happens when you don’t send the right credentials to access an API.",
        "403" : "The resource you’re trying to access is forbidden: you don’t have the right permissions to see it.",
        "404" : "The resource you tried to access wasn’t found on the server.",
        "405" : "To be determined",
        "503" : "The server is not ready to handle the request."
    }

    ###########################################################
    # Initializing the API authentication request             #
    ###########################################################
    header = {'Content-Type': 'application/x-www-form-urlencoded'}
    if authType == "APIClientID":
        url = "https://account.demandware.com/dwsso/oauth2/access_token"
        url_params = {'client_id': sfcc_client_id, 'grant_type': 'client_credentials'}
        authen = HTTPBasicAuth(sfcc_client_id, sfcc_secret)
    elif authType == "BusinessManager":
        match instance:
            case "prd":
                url = "https://production-eu02-magasin.demandware.net/dw/oauth2/access_token?client_id=" + sfcc_client_id
            case "stg":
                url = "https://staging-eu02-magasin.demandware.net/dw/oauth2/access_token?client_id=" + sfcc_client_id
            case "dev":
                url = "https://development-eu02-magasin.demandware.net/dw/oauth2/access_token?client_id=" + sfcc_client_id
        secret = f"{sfcc_password}:{sfcc_secret}"
        
        url_params = {'client_id': sfcc_client_id, 'grant_type': 'urn:demandware:params:oauth:grant-type:client-id:dwsid:dwsecuretoken'}
        authen = HTTPBasicAuth(sfcc_user, secret)

    ###########################################################
    # Calling the API authentication request                  #
    ###########################################################
    response = requests.post(url, auth = authen, params = url_params, headers = header)

    ######################################
    # Getting the status for API REQUEST #
    ######################################
    API_status_code = str(response.status_code)
    message = "Response: " + API_status_code + " - " + API_status_code_texts[API_status_code]
    #print("\n"+message+"\n")

    #####################################################
    # Loads the JSON response text from the API request #
    #####################################################
    json_response = json.loads(response.text)
    #print('json_response: '+str(json_response)+'\n')

    #####################################
    # Initializing the API Token request #
    #####################################
    try:
        access_token = json_response['access_token']
        return access_token, message
    except:
        access_token = "Error"
        return access_token, message
    
if __name__ == "__main__":
    # Example usage
    instance = "dev" # "prd" or "stg" or "dev"
    sfcc_authType = "APIClientID" # "APIClientID" or "BusinessManager"
    sfcc_client_id = config.sfcc_client_id
    sfcc_secret = config.sfcc_secret
    sfcc_user = config.sfcc_user
    sfcc_password = config.sfcc_password
    
    access_token, message = OCAPI_Authenticate_OAuth2(instance, sfcc_authType, sfcc_client_id, sfcc_secret)
    print(f"Access token: {access_token}")
    print(f"Message: {message}")

    sfcc_authType = "BusinessManager" # "APIClientID" or "BusinessManager"
    
    access_token, message = OCAPI_Authenticate_OAuth2(instance, sfcc_authType, sfcc_client_id, sfcc_secret, sfcc_user, sfcc_password)
    print(f"Access token: {access_token}")
    print(f"Message: {message}")
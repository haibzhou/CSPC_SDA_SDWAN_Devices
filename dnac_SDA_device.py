import requests
import base64
import json
import socket

# Replace these with your actual DNAC credentials and URL
DNAC_BASE_URL = "https://<your_dnac_ip_or_hostname>"
USERNAME = "username"
PASSWORD = "password"




def get_auth_token(base_url, username, password):
    """
    Function to get the authentication token from DNAC
    """
    url = f"{base_url}/dna/system/api/v1/auth/token"
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_base64}'
    }

    response = requests.post(url, headers=headers, verify=False)
    response.raise_for_status()
    
    token = response.json()["Token"]
    return token

def get_devices(base_url, token):
    """
    Function to get the list of devices from DNAC
    """
    url = f"{base_url}/dna/intent/api/v1/network-device"
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': token
    }
    #limit the number of devices to 10  
    response = requests.get(url, headers=headers, verify=False)
    
    response.raise_for_status()
    
    devices = response.json()
    return devices

def get_all_devices(dnac_url, token):
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': token
    }
    devices = []
    offset = 1
    limit = 500  # You can increase this limit, but 500 is a reasonable default

    while True:
        # API endpoint with pagination parameters
        url = f"{dnac_url}/dna/intent/api/v1/network-device?offset={offset}&limit={limit}"

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Check for HTTP errors

        data = response.json()
        devices.extend(data['response'])

        # Check if more devices are available
        if len(data['response']) < limit:
            break  # No more devices to fetch

        # Move to the next batch
        offset += limit

        # Stop the loop if we have retrieved 10,000 devices
        if len(devices) >= 20000:
            devices = devices[:20000]  # Trim the list to exactly 10,000 devices
            break
    #print(f"Total devices: {len(devices)}")
    #print(json.dumps(devices, indent=4))
    return devices




def main():
    """
    Main function to get and print device data
    """
    device_role = ["WE", "WC", "WM", "WV", "TR", "TE", "RR", "CC", "BN", "IN", "EN", "XN", "PN", "SN", "DC", "DS", "DL", "DE", "FW", "AP", "WC", "VG", "VR", "VS", "RN"]

    try:
        token = get_auth_token(DNAC_BASE_URL, USERNAME, PASSWORD)
        devices = get_all_devices(DNAC_BASE_URL, token)
        #print(json.dumps(devices, indent=4))

        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    f = open("dnac_SDA_device1.txt", "w")
    for device in devices:
        if (device["family"] != "Unified AP") and (device["hostname"] != None):
            #some management IP addresses are in DNS domanin format, so we need to convert them to IP addresses
            if device["managementIpAddress"].startswith("10.") or device["managementIpAddress"].startswith("172.") or device["managementIpAddress"].startswith("192."):
                #use regular expression to filter out if hostname has "-" and any of the device role, do not use re
                    if (not device["hostname"].startswith("SN")) and ("-" in device["hostname"]) and any(role in device["hostname"] for role in device_role):
                        #split device["hostname"] to get the hostname without domain name
                        print(f'{device["hostname"].split(".")[0]}, {device["managementIpAddress"]},{device["platformId"]}')
                        #print(f'{device["hostname"]}, {device["managementIpAddress"]},{device["platformId"]}')
                        #save to file
                        #split device["hostname"] to get the hostname without domain name
                        f.write(f'{device["hostname"].split(".")[0]},{device["managementIpAddress"]},{device["platformId"]}\n')
                        #f.write(f'{device["hostname"]},{device["managementIpAddress"]}\n')

            else:
                try:
                    socket.gethostbyname(device["managementIpAddress"])
                    #use regular expression to filter out if hostname has "-" and any of the device role, do not use re
                    if (not device["hostname"].startswith("SN")) and ("-" in device["hostname"]) and any(role in device["hostname"] for role in device_role):
                        #split device["hostname"] to get the hostname without domain name
                        print(f'{device["hostname"].split(".")[0]}, {socket.gethostbyname(device["managementIpAddress"])},{device["platformId"]}')
                        #print(f'Hostname: {device["hostname"]}, IP: {socket.gethostbyname(device["managementIpAddress"])}, Family: {device["platformId"]}')
                        #save to file
                        #f.write(f'{device["hostname"]},{socket.gethostbyname(device["managementIpAddress"])},{device["platformId"]}\n')
                        #split device["hostname"] to get the hostname without domain name
                        f.write(f'{device["hostname"].split(".")[0]},{socket.gethostbyname(device["managementIpAddress"])},{device["platformId"]}\n')
                        #f.write(f'{device["hostname"]},{socket.gethostbyname(device["managementIpAddress"])}\n')
                except socket.gaierror:
                    continue

            #print hostname, management IP, platform ID 
            #print(f'Hostname: {device["hostname"]}, IP: {device["managementIpAddress"]}, Family: {device["platformId"]}')
    
if __name__ == "__main__":
    main()

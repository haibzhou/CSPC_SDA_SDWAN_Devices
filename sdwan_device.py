import requests

# vManage details
vmanage_ip = "<your_vmanage_ip>"
username = "username"
password = "password"


# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# API URLs
login_url = f"https://{vmanage_ip}/j_security_check"
device_url = f"https://{vmanage_ip}/dataservice/device"

# Start a session
session = requests.session()

# Step 1: Authenticate and get a session
payload = {
    "j_username": username,
    "j_password": password
}

response = session.post(login_url, data=payload, verify=False)

if response.status_code != 200 or "Set-Cookie" not in response.headers:
    print("Login failed! Check your credentials.")
    exit()

print("Login successful!")

#open file for write
f = open("sdwan_device.txt", "w")

# Step 2: Get device list
device_response = session.get(device_url, verify=False)

if device_response.status_code == 200:
    devices = device_response.json().get("data", [])
    print("Device List:")
    for device in devices:
        print(f"{device.get('host-name')}, {device.get('system-ip')}, {device.get('device-type')}")
        #save it to file
        f.write(f"{device.get('host-name')}, {device.get('system-ip')}\n")
else:
    print(f"Failed to fetch device list: {device_response.text}")

f.close()
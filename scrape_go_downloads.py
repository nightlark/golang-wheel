import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin

# Send a GET request to the website
url = 'https://go.dev/dl/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Regular expression pattern for matching the div id format
pattern = re.compile(r'^go\d+(\..+)?$')

data = {}

# Find all the divs with appropriate id format
divs = soup.find_all('div', id=pattern)

# Iterate over each div
for div in divs:
    # Find the table within the current div
    table = div.find('table', class_='downloadtable')

    # Get the id from the div
    id_ = div.get('id')

    # Skip if table is not found or id does not match the desired format
    if not table or not pattern.match(id_):
        continue

    # Find all the rows in the table
    rows = table.find_all('tr')

    # Initialize the entries for the current id
    data[id_] = []

    # Iterate over each row, skipping rows within the <thead> tags and rows with class "js-togglePorts"
    for row in rows:
        if row.find_parent('thead') or 'js-togglePorts' in row.get('class', []):
            continue

        columns = row.find_all('td')

        # Extract the desired fields from each column
        file_name = columns[0].find('a').text
        download_url = urljoin(url, columns[0].find('a')['href'])
        kind = columns[1].text
        os = columns[2].text
        arch = columns[3].text
        size = columns[4].text
        sha256_checksum = columns[5].text

        # Create a dictionary for the current entry
        entry = {
            'file_name': file_name,
            'download_url': download_url,
            'kind': kind,
            'os': os,
            'arch': arch,
            'size': size,
            'sha256_checksum': sha256_checksum
        }

        # Add the entry to the entries for the current id
        data[id_].append(entry)


def find_latest_version(json_data, ignore_beta_rc=False):
    data = json.loads(json_data)
    version_pattern = re.compile(r'^go(\d+(\.\d+)*)(beta(\d+)|rc(\d+))?$')

    latest_version = None
    latest_version_key = None

    for key in data.keys():
        match = version_pattern.match(key)
        if match:
            version = match.group(1)
            beta = match.group(4)
            rc = match.group(5)

            if not ignore_beta_rc or (ignore_beta_rc and not beta and not rc):
                if not latest_version or is_newer_version(version, beta, rc, latest_version):
                    latest_version = version
                    latest_version_key = key

    return latest_version_key

def is_newer_version(version, beta, rc, latest_version):
    version_parts = [int(part) for part in version.split('.')]
    latest_version_parts = [int(part) for part in latest_version.split('.')]

    if version_parts > latest_version_parts:
        return True
    elif version_parts < latest_version_parts:
        return False

    if not beta and not rc:
        return False

    latest_beta = get_beta_number(latest_version)
    latest_rc = get_rc_number(latest_version)

    if beta and not rc and not latest_version.endswith('rc'):
        return True
    elif rc and not latest_version.endswith('rc'):
        return True
    elif beta and latest_rc:
        return False
    elif beta and latest_beta and int(beta) > int(latest_beta):
        return True
    elif rc and latest_rc and int(rc) > int(latest_rc):
        return True

    return False

def get_beta_number(version):
    beta_match = re.search(r'beta(\d+)', version)
    if beta_match:
        return beta_match.group(1)
    return None

def get_rc_number(version):
    rc_match = re.search(r'rc(\d+)', version)
    if rc_match:
        return rc_match.group(1)
    return None

# Convert the data dictionary to a JSON object
json_data = json.dumps(data, indent=4)

# Assuming json_data contains the JSON object
latest_version_key = find_latest_version(json_data, ignore_beta_rc=True)
print(f"The key for the latest version is: {latest_version_key}")

# Convert the data dictionary to a JSON object
json_data = json.dumps(data[latest_version_key], indent=4)

with open("go_downloads.json", "w") as dl_list:
    dl_list.write(json_data)



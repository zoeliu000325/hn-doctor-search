import requests
import json
import os


def fetch_data(search_text_values):
    url = 'https://www.healthnet.com/app/providerSearch/solrProxy'
    # Build fq parameters dynamically based on search_text_values
    fq_params = [
        '((*:* NOT DISPLAY_END_DATE:*) OR DISPLAY_START_DATE:[2024-08-01T12:00:00Z-1DAY TO *])',
        'PRV_TYPE:I',
        'product_code:1CC',
        '-SPECIALTY:UNKNOWN',
        '-SPECIALTY:"UNAVAILABLE FOR DATA ENTRY"'
    ]
    fq_params.extend([f'SEARCH_TEXT:*{text}*' for text in search_text_values])

    params = {
        'fq': fq_params,
        'q': 'state:"CA"',
        'wt': 'json',
        'facet': 'true',
        'facet.field': [
            'PRV_TYPE',
            'SPECIALTY',
            'MEDICAL_GROUP',
            'LANGUAGE',
            'STAFFLANGUAGE',
            'PRODUCT_EXT',
            'MEDICAL_GROUP',
            'MEDICAL_GROUP_ID',
            'HOSPITAL',
            'SERVICE'
        ],
        'facet.mincount': '1',
        'facet.sort': 'indext',
        'facet.limit': '600',
        'fl': 'listing_idx,PRV_ID,PRV_ID_TYPE,PRV_FULL_NAME,score,SPECIALTY,PRV_TYPE,medical_plan_count,state,location,PRODUCT_NAME,product_code,street_1,street_2,suite,city,state,zip,county,PRODUCT_START_DATE,IS_HMO,ORIG_PRV_TYPE,pcp_spec_flag,accept_new_pat_flag,telemedicine_capable,telemedicine_indicator,onsite_indicator,ENROLLMENTID,limit_by_age_min,limit_by_age_max,PHONE_NUM,phy_degree,phy_gender,MEDICAL_GROUP,medicaid_ffs_flag,provider_ind,accreditation,future_eff_date,future_exp_date,effDateCount,expDateCount',
        'group.format': 'grouped',
        'group.limit': '30',
        'group.sort': 'score asc,product_code asc',
        'group': 'true', # may have different address etc.
        'group.field': 'PRV_ID_TYPE',
        'group.ngroups': 'true',
        'group.truncate': 'false',
        'sort': 'PRV_FULL_NAME_SORT asc',
        'json.wrf': '__gwt_jsonp__.P10.onSuccess',
        'start': '0',
        'rows': '150' # return result count.
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Cookie': '_gcl_au=1.1.1533873459.1729490702; _ga=GA1.1.1690030993.1729490702; ...',  # Include other cookie values as needed
        'Referer': 'https://www.healthnet.com/portal/providerSearch.action',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    groups = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response = response.text[len('__gwt_jsonp__.P10.onSuccess('):-1]
        response_json = json.loads(response)
        groups = response_json['grouped']['PRV_ID_TYPE']['groups']

    except Exception as e:
        print('\033[7m{}\033[0m'.format("An error occurred, please try again. If the problem persists, contact the administrator."))
        print(f"Error details: {e}")

    return groups

def traverse_group(data):
    for group in data:
        # print doctor name
        doctor_name = group['doclist']['docs'][0]['PRV_FULL_NAME']
        text = '\033[7m{}\033[0m'.format(doctor_name) # highlight
        print(text)
        
        addresses = set()
        medical_groups = set()
        for doc in group['doclist']['docs']:
            addresses.add(doc['street_1'] + ', ' + doc['county'] + ', ' + doc['state'] + ' ' + doc['zip'])
            medical_groups.add(doc['MEDICAL_GROUP'])
        
        print("Address:")
        for address in addresses:
            print('    ' + address)
        print("Medical Group:")
        for medical_group in medical_groups:
            print('    ' + medical_group)

        print()

def search_doc(search_text_values):
    data = fetch_data(search_text_values)
    if len(data) == 0:
        print("No results found.")
    else:
        traverse_group(data)

    # json.dump(data, open('data.json', 'w'), indent=4)

if __name__ == "__main__":
    while True:
        user_input = input("Please input doctor's name:\n")
        os.system('cls') # clear history output
        print(f"Searching for '{user_input}'")
        search_text_values = user_input.split()
        search_doc(search_text_values)
        print()

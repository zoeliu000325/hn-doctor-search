import requests
import json
import os
import streamlit as st

def fetch_data(search_text_values):
    url = 'https://www.healthnet.com/app/providerSearch/solrProxy'
    
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
        'group.limit': '1000',
        'group.sort': 'score asc,product_code asc',
        'group': 'true',
        'group.field': 'PRV_ID_TYPE',
        'group.ngroups': 'true',
        'group.truncate': 'false',
        'sort': 'PRV_FULL_NAME_SORT asc',
        'json.wrf': '__gwt_jsonp__.P10.onSuccess',
        'start': '0',
        'rows': '150'
    }

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Referer': 'https://www.healthnet.com/portal/providerSearch.action',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    }

    groups = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response = response.text[len('__gwt_jsonp__.P10.onSuccess('):-1]
        response_json = json.loads(response)
        groups = response_json['grouped']['PRV_ID_TYPE']['groups']
    except Exception as e:
        st.error(f"An error occurred: {e}")

    return groups

def search_doc(search_text_values):
    data = fetch_data(search_text_values)
    if len(data) == 0:
        st.write("No results found.")
    else:
        for group in data:
            doctor_name = group['doclist']['docs'][0]['PRV_FULL_NAME']
            st.write(f"**Doctor: {doctor_name}**")

            addresses = set(doc['street_1'] + ', ' + doc['county'] + ', ' + doc['state'] + ' ' + doc['zip'] for doc in group['doclist']['docs'])
            medical_groups = set(doc['MEDICAL_GROUP'] for doc in group['doclist']['docs'])
            
            st.write("**Addresses:**")
            for address in addresses:
                st.write(f" - {address}")

            st.write("**Medical Groups:**")
            for group in medical_groups:
                st.write(f" - {group}")
            st.write("---")

# Streamlit UI
st.title("Doctor Search")

# Input text box and button
search_text = st.text_input("Please input doctor's name:")
if st.button("Search"):
    search_text_values = search_text.split()
    st.write(f"Searching for '{search_text}'")
    search_doc(search_text_values)

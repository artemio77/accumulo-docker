import json
import os
import re

import requests
from bs4 import BeautifulSoup


def parse_edgar_filing(file_path):
    parsed_data = {}

    with open(file_path, 'r') as file:
        filing_content = file.read()

        # Extract the document type
        doc_type_match = re.search(r"<TYPE>(.*?)\n", filing_content)
        if doc_type_match:
            parsed_data['documentType'] = doc_type_match.group(1).strip()

        # Extract the filing date
        filing_date_match = re.search(r"CONFORMED PERIOD OF REPORT:\s*(\d+)", filing_content)
        if filing_date_match:
            parsed_data['fillingDate'] = filing_date_match.group(1)

        # Extract the company name
        company_name_match = re.search(r"COMPANY CONFORMED NAME:\s*(.*?)\s", filing_content)
        if company_name_match:
            parsed_data['companyName'] = company_name_match.group(1)

        # Extract the file text
        file_text_match = re.search(r"<TEXT>(.*?)<\/TEXT>", filing_content, re.DOTALL)
        contractions = {
            "ain't": "is not",
            "aren't": "are not",
            "can't": "cannot",
            "can't've": "cannot have",
            "'cause": "because",
            "could've": "could have",
            "couldn't": "could not",
            "couldn't've": "could not have",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hadn't've": "had not have",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'd've": "he would have",
            "he'll": "he will",
            "he'll've": "he he will have",
            "he's": "he is",
            "how'd": "how did",
            "how'd'y": "how do you",
            "how'll": "how will",
            "how's": "how is",
            "I'd": "I would",
            "I'd've": "I would have",
            "I'll": "I will",
            "I'll've": "I will have",
            "I'm": "I am",
            "I've": "I have",
            "i'd": "i would",
            "i'd've": "i would have",
            "i'll": "i will",
            "i'll've": "i will have",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",
            "it'd've": "it would have",
            "it'll": "it will",
            "it'll've": "it will have",
            "it's": "it is",
            "let's": "let us",
            "ma'am": "madam",
            "mayn't": "may not",
            "might've": "might have",
            "mightn't": "might not",
            "mightn't've": "might not have",
            "must've": "must have",
            "mustn't": "must not",
            "mustn't've": "must not have",
            "needn't": "need not",
            "needn't've": "need not have",
            "o'clock": "of the clock",
            "oughtn't": "ought not",
            "oughtn't've": "ought not have",
            "shan't": "shall not",
            "sha'n't": "shall not",
            "shan't've": "shall not have",
            "she'd": "she would",
            "she'd've": "she would have",
            "she'll": "she will",
            "she'll've": "she will have",
            "she's": "she is",
            "should've": "should have",
            "shouldn't": "should not",
            "shouldn't've": "should not have",
            "so've": "so have",
            "so's": "so as",
            "that'd": "that would",
            "that'd've": "that would have",
            "that's": "that is",
            "there'd": "there would",
            "there'd've": "there would have",
            "there's": "there is",
            "they'd": "they would",
            "they'd've": "they would have",
            "they'll": "they will",
            "they'll've": "they will have",
            "they're": "they are",
            "they've": "they have",
            "to've": "to have",
            "wasn't": "was not",
            "we'd": "we would",
            "we'd've": "we would have",
            "we'll": "we will",
            "we'll've": "we will have",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what will",
            "what'll've": "what will have",
            "what're": "what are",
            "what's": "what is",
            "what've": "what have",
            "when's": "when is",
            "when've": "when have",
            "where'd": "where did",
            "where's": "where is",
            "where've": "where have",
            "who'll": "who will",
            "who'll've": "who will have",
            "who's": "who is",
            "who've": "who have",
            "why's": "why is",
            "why've": "why have",
            "will've": "will have",
            "won't": "will not",
            "won't've": "will not have",
            "would've": "would have",
            "wouldn't": "would not",
            "wouldn't've": "would not have",
            "y'all": "you all",
            "y'all'd": "you all would",
            "y'all'd've": "you all would have",
            "y'all're": "you all are",
            "y'all've": "you all have",
            "you'd": "you would",
            "you'd've": "you would have",
            "you'll": "you will",
            "you'll've": "you will have",
            "you're": "you are",
            "you've": "you have"
        }
        if file_text_match:
            file_text = file_text_match.group(1)

            # Remove HTML tags and entities
            cleaned_text = re.sub(r'<.*?>', '', file_text)
            cleaned_text = re.sub(r'&\w+;', '', cleaned_text)
            cleaned_text = re.sub('\n{1,}', ' ', cleaned_text)
            cleaned_text = re.sub("\s{1,}", " ", cleaned_text)

            parsed_data['text'] = cleaned_text.strip()

    return parsed_data


def save_parsed_data_as_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True)


def save_txt_file(data, file_path):
    with open(file_path, 'w') as file:
        file.write(data)


def remove_text_in_none_display_div(html_text):
    updated_html_text = re.sub(r'<div\s*style="[^"]*display:\s*none[^"]*".*?</div>',
                               lambda match: match.group(0).replace(match.group(0), '<div></div>'),
                               html_text,
                               flags=re.IGNORECASE | re.DOTALL)

    return updated_html_text


def download_filings_by_ticker(ticker, filing_type):
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    search_endpoint = f"{base_url}?action=getcompany&CIK={ticker}&type={filing_type}&count=10"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_endpoint, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='tableFile2')
        filings = table.find_all('tr')

        if len(filings) > 1:
            filing_row = filings[1]
            filing_cols = filing_row.find_all('td')
            filing_href = filing_cols[1].find('a')['href']
            filing_details_url = f"https://www.sec.gov{filing_href}"

            filing_details_response = requests.get(filing_details_url, headers=headers)
            if filing_details_response.status_code == 200:
                filing_details_soup = BeautifulSoup(filing_details_response.text, 'html.parser')
                filing_text_urls = filing_details_soup.find_all('a', href=re.compile('.*txt$'))
                if filing_text_urls:
                    download_url = "https://www.sec.gov" + filing_text_urls[0]['href']

                    file_name = f"{ticker}_{filing_type}.txt"
                    save_folder = os.path.join(os.getcwd(), f"data/raw/{ticker}")
                    os.makedirs(save_folder, exist_ok=True)
                    save_path = os.path.join(save_folder, file_name)

                    filing_response = requests.get(download_url, headers=headers)
                    if filing_response.status_code == 200:
                        save_txt_file(remove_text_in_none_display_div(filing_response.text), save_path)
                        print(f"Downloaded {filing_type} filing for {ticker} successfully.")

                        # Parse the downloaded filing
                        parsed_data = parse_edgar_filing(save_path)
                        return parsed_data
                    else:
                        print(f"Failed to download {filing_type} filing for {ticker}.")
                else:
                    print(f"No text filing found for {filing_type} filing of {ticker}.")
            else:
                print(f"Failed to retrieve filing details for {ticker}.")
        else:
            print(f"No {filing_type} filings found for {ticker}.")
    else:
        print(f"Failed to retrieve filing search results for {ticker}.")

    return None


if __name__ == '__main__':
    # Example usage
    ticker = "SNOW"
    filing_type_10k = "10-K"
    filing_type_10q = "10-Q"
    filing_type_8k = "8-K"

    parsed_data_10k = download_filings_by_ticker(ticker, filing_type_10k)
    parsed_data_10q = download_filings_by_ticker(ticker, filing_type_10q)
    parsed_data_8k = download_filings_by_ticker(ticker, filing_type_8k)

    if parsed_data_10k:
        save_folder = os.path.join(os.getcwd(), f"data/result/{ticker}")
        os.makedirs(save_folder, exist_ok=True)
        save_parsed_data_as_json(parsed_data_10k, os.path.join(save_folder, f"{ticker}-{filing_type_10k}.json"))

    if parsed_data_10q:
        save_folder = os.path.join(os.getcwd(), f"data/result/{ticker}")
        os.makedirs(save_folder, exist_ok=True)
        save_parsed_data_as_json(parsed_data_10q, os.path.join(save_folder, f"{ticker}-{filing_type_10q}.json"))

    if parsed_data_8k:
        save_folder = os.path.join(os.getcwd(), f"data/result/{ticker}")
        os.makedirs(save_folder, exist_ok=True)
        save_parsed_data_as_json(parsed_data_8k, os.path.join(save_folder, f"{ticker}-{filing_type_8k}.json"))

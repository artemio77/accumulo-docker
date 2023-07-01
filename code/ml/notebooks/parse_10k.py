import requests
import re
from bs4 import BeautifulSoup


def parse_10k_filing(text, section_name):
    section_mapping = {
        "1": "Business",
        "1A": "Risk Factors",
        "1B": "Unresolved Staff Comments",
        "2": "Properties",
        "3": "Legal Proceedings",
        "4": "Mine Safety Disclosures",
        "5": "Market for Registrant’s Common Equity, Related Stockholder Matters and Issuer Purchases of Equity Securities",
        "6": "Selected Financial Data (prior to February 2021)",
        "7": "Management’s Discussion and Analysis of Financial Condition and Results of Operations",
        "7A": "Quantitative and Qualitative Disclosures about Market Risk",
        "8": "Financial Statements and Supplementary Data",
        "9": "Changes in and Disagreements with Accountants on Accounting and Financial Disclosure",
        "9A": "Controls and Procedures",
        "9B": "Other Information",
        "10": "Directors, Executive Officers and Corporate Governance",
        "11": "Executive Compensation",
        "12": "Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
        "13": "Certain Relationships and Related Transactions, and Director Independence",
        "14": "Principal Accountant Fees and Services"
    }

    section_start = re.compile(fr"item\s*{section_name}(?![A-Za-z])", re.IGNORECASE)
    section_end = re.compile(fr"item\s*(?:{section_name[:-1]}\s*[^A-Za-z]?)", re.IGNORECASE)

    try:
        section_text = extract_text(text, section_start, section_end)
    except:
        section_text = "Something went wrong!"

    section_title = section_mapping.get(section_name, "Unknown Section")

    data = {
        "title": section_title,
        "text": section_text
    }
    return data


def get_text(link):
    page = requests.get(link, headers={'User-Agent': 'Mozilla'})
    html = BeautifulSoup(page.content, "html.parser")
    text = html.get_text()
    text = re.sub(r'\s+', ' ', text)  # Remove excess white spaces
    return text


def extract_text(text, section_start, section_end):
    starts = [i.start() for i in section_start.finditer(text)]
    ends = [i.start() for i in section_end.finditer(text)]
    positions = []
    for s in starts:
        control = 0
        for e in ends:
            if control == 0:
                if s < e:
                    control = 1
                    positions.append([s, e])
    section_length = 0
    section_position = []
    for p in positions:
        if (p[1] - p[0]) > section_length:
            section_length = p[1] - p[0]
            section_position = p

    section_text = text[section_position[0]:section_position[1]]

    return section_text


def main():
    filing_url_10k = "https://www.sec.gov/Archives/edgar/data/831001/000083100123000037/c-20221231.htm"
    section_name = "1"

    filing_text = get_text(filing_url_10k)
    parsed_data = parse_10k_filing(filing_text, section_name)

    print(f"Section: {parsed_data['title']}")
    print(parsed_data['text'])


if __name__ == "__main__":
    main()

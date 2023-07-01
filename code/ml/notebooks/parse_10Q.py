import re
from typing import Dict

import requests
from bs4 import BeautifulSoup

SECTION_KEYS = [
    "1-1",
    "1-2",
    "1-3",
    "1-4",
    "2-1",
    "2-1A",
    "2-2",
    "2-3",
    "2-4",
    "2-5",
    "2-6"
]

SECTION_MAPPING = {
    "1-1": {"start": "ITEM 1.", "end": "ITEM"},
    "1-2": {"start": "ITEM 2.", "end": "ITEM"},
    "1-3": {"start": "ITEM 3.", "end": "ITEM"},
    "1-4": {"start": "ITEM 4.", "end": "PART II."},
    "2-1": {"start": "ITEM 1.", "end": "ITEM"},
    "2-1A": {"start": "ITEM 1A.", "end": "ITEM"},
    "2-2": {"start": "ITEM 2.", "end": "ITEM"},
    "2-3": {"start": "ITEM 3.", "end": "ITEM"},
    "2-4": {"start": "ITEM 4.", "end": "ITEM"},
    "2-5": {"start": "ITEM 5.", "end": "ITEM"},
    "2-6": {"start": "ITEM 6.", "end": "SIGNATURE"},
    "2-7": {"start": "SIGNATURE", "end": ""}
}


def parse_10q_filing(text, part, section_n):
    section_key = part + "-" + section_n
    section_name = SECTION_MAPPING.get(section_key, "Unknown Section")

    section_start = re.compile(fr"(?:{section_name.get('start')}[:-]?\s*[^A-Za-z]?)", re.IGNORECASE)
    section_end = re.compile(fr"(?:{section_name.get('end')}[:-]?\s*[^A-Za-z]?)", re.IGNORECASE)

    part_name = ""
    next_part_name = ""
    if part == "1":
        part_name = "PART I"
        next_part_name = "PART II"
    else:
        part_name = "PART II"
        next_part_name = "SIGNATURE"
    try:
        section_text = extract_text(text, part_name, next_part_name, section_start, section_end)
    except Exception as e:
        print(e)
        section_text = f"None."

    data = {
        "title": section_name,
        "text": section_text
    }
    return data


def next_section_name(key: str, elements: Dict[str, str]):
    ki = dict()
    ik = dict()
    for i, k in enumerate(elements):
        ki[k] = i  # dictionary index_of_key
        ik[i] = k  # dictionary key_of_index
    offset = 1  # (1 for next key, but can be any existing distance)

    # Get next key in Dictionary
    index_of_key = ki[key]
    index_of_next_key = index_of_key + offset
    next_key = ik[index_of_next_key] if index_of_next_key in ik else None
    return elements.get(next_key)


def get_text(link):
    page = requests.get(link, headers={'User-Agent': 'Mozilla'})
    html = BeautifulSoup(page.content, "html.parser")
    text = html.get_text()  # Remove excess white spaces
    return text


def trim_array(arr, length):
    if len(arr) > length:
        return arr[:length]
    else:
        return arr


def extract_text(text, part_name, next_part_name, section_start, section_end):
    toc_start_pattern = 'TABLE OF CONTENTS'
    toc_end_pattern = 'PART I'

    # Find the start and end indexes
    toc_start_index = re.search(toc_start_pattern, text).start()
    toc_end_index = find_after_index(text, toc_end_pattern, toc_start_index, False)[0]

    # Extract the start and end indexes
    part_list = find_after_index(text, part_name, toc_end_index, True)
    part_index = part_list[len(part_list) - 1]
    next_part_index = find_after_index(text, next_part_name, toc_end_index, True)[0]

    starts = []
    for i in section_start.finditer(text):
        index = i.start()
        if toc_end_index < index and part_index < index <= next_part_index:
            starts.append(index)
    ends = []
    for i in section_end.finditer(text):
        index = i.start()
        if any(i < index for i in starts) and part_index < index <= next_part_index:
            ends.append(index)
            break

    starts = trim_array(starts, len(ends))
    ends = trim_array(ends, len(starts))
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
        section_position.append(p)
    section_text = ""
    for p in section_position:
        section_text += text[p[0]:p[1]]

    return section_text


def find_after_index(text, pattern, start_index, case_sensitive: bool = True):
    if case_sensitive:
        matched_indexes = [i.start() for i in re.compile(pattern, re.IGNORECASE).finditer(text)]
        filtered_indexes = [i for i in filter(lambda current_index: current_index > start_index, matched_indexes)]
        return filtered_indexes
    else:
        matched_indexes = [i.start() for i in re.compile(pattern).finditer(text)]
        filtered_indexes = [i for i in filter(lambda current_index: current_index > start_index, matched_indexes)]
        return filtered_indexes


def main():
    # CF
    filing_url = "https://www.sec.gov/Archives/edgar/data/1324404/000132440423000012/0001324404-23-000012.txt"
    # SNOW
    # filing_url = "https://www.sec.gov/Archives/edgar/data/1640147/000164014723000102/0001640147-23-000102.txt"
    # C
    # filing_url = "https://www.sec.gov/Archives/edgar/data/320193/000032019323000064/0000320193-23-000064.txt"
    part = "2"
    section_name = "2"

    filing_text = get_text(filing_url)
    parsed_data = parse_10q_filing(filing_text, part, section_name)

    print(f"Section: {parsed_data['title']}")
    print(parsed_data['text'])


if __name__ == "__main__":
    main()

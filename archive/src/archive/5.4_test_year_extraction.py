import re

def extract_mentioned_years(text):
    matches = re.findall(r"\b(20\d{2})-(\d{2})\b", text)
    years = {f"{start}-{end}" for start, end in matches}
    return sorted(years)


test_text = """the target of 4.1 per cent fiscal deficit is indeed daunting. Difficult, as it may appear,
I have decided to accept this target as a challenge. One fails only when one stops
trying. My Road map for fiscal consolidation is a fiscal deficit of 3.6 per cent for
2015-16 and 3 per cent for 2016-17."""

print(extract_mentioned_years(test_text))
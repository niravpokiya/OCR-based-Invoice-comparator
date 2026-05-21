import re
import unicodedata
from datetime import datetime
from difflib import SequenceMatcher

import pytesseract
from PIL import Image
from pdf2image import convert_from_path

from config import POPPLER_PATH, TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


CRITICAL_FIELDS = [
    "invoice_number",
    "invoice_date",
    "vendor_name",
    "buyer_name",
    "gst_vat_number",
    "pan_number",
    "total_amount",
    "gross_weight",
    "net_weight",
    "country_destination",
    "port_loading",
    "port_discharge",
    "package_count",
]


def extract_text_from_image(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)


def extract_text_from_pdf(pdf_path):
    if POPPLER_PATH:
        images = convert_from_path(
            pdf_path,
            poppler_path=POPPLER_PATH,
            dpi=300
        )
    else:
        images = convert_from_path(pdf_path, dpi=300)

    text = []

    for image in images:
        extracted = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 6"
        )
        text.append(extracted)

    return "\n".join(text)


def extract_invoice_fields(raw_text):
    text = normalize_text(raw_text)

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    fields = {
        "invoice_number": extract_invoice_number(lines),
        "invoice_date": extract_invoice_date(lines),
        "vendor_name": extract_vendor_name(lines),
        "buyer_name": extract_buyer_name(lines),
        "gst_vat_number": extract_gstin(text),
        "pan_number": extract_pan(text),
        "total_amount": extract_total_amount(text),
        "gross_weight": extract_gross_weight(text),
        "net_weight": extract_net_weight(text),
        "country_destination": extract_destination_country(lines),
        "port_loading": extract_port_loading(lines),
        "port_discharge": extract_port_discharge(lines),
        "package_count": extract_package_count(text),
    }

    print(fields)

    return fields


# =========================
# EXTRACTION FUNCTIONS
# =========================

def extract_invoice_number(lines):

    patterns = [
        r'invoice\s*no\.?\s*[:\-]?\s*([A-Z0-9/\-]+)',
        r'inv\.?\s*no\.?\s*[:\-]?\s*([A-Z0-9/\-]+)',
        r'exp/\d+/\d{2}-\d{2}',
    ]

    ignore_words = {
        "igst",
        "innsa",
        "details",
        "item",
        "date"
    }

    for line in lines:

        clean = line.strip()

        for pattern in patterns:

            match = re.search(
                pattern,
                clean,
                re.IGNORECASE
            )

            if match:

                value = match.group(1) if match.lastindex else match.group()

                value = value.strip()

                if value.lower() not in ignore_words:
                    return value

    return None


def extract_invoice_date(lines):
    date_patterns = [
        r'\d{2}[/-]\d{2}[/-]\d{4}',
        r'\d{2}-[A-Za-z]{3}-\d{4}'
    ]

    keywords = [
        "invoice date",
        "inv date"
    ]

    for i, line in enumerate(lines):

        lower = line.lower()

        if any(k in lower for k in keywords):

            for p in date_patterns:
                match = re.search(p, line)
                if match:
                    return normalize_date(match.group())

            if i + 1 < len(lines):
                next_line = lines[i + 1]

                for p in date_patterns:
                    match = re.search(p, next_line)
                    if match:
                        return normalize_date(match.group())

    return None


def extract_vendor_name(lines):

    patterns = [
        r'exporter\s*:?\s*(.+)',
        r'vendor\s*:?\s*(.+)',
        r'supplier\s*:?\s*(.+)'
    ]

    bad_words = [
        "invoice",
        "date",
        "gst",
        "weight",
        "port",
        "printed",
        "checklist"
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if match:

                candidate = match.group(1).strip()

                if (
                    len(candidate) > 5
                    and not any(
                        w in candidate.lower()
                        for w in bad_words
                    )
                ):
                    return candidate

    return None
def extract_destination_country(lines):

    for i, line in enumerate(lines):

        lower = line.lower()

        if (
            "country of final destination" in lower
            or "discharge country" in lower
            or "country of dest" in lower
        ):

            countries = [
                "romania",
                "india",
                "usa",
                "germany",
                "france",
                "italy",
                "uk"
            ]

            for country in countries:
                if country in lower:
                    return country.title()

            for j in range(i + 1, min(i + 4, len(lines))):

                candidate = lines[j].strip()

                if (
                    candidate.isalpha()
                    and len(candidate) > 3
                ):
                    return candidate.title()

    return None
def extract_port_loading(lines):

    ignore_words = [
        "weight",
        "gross",
        "net",
        "description",
        "delivery",
        "invoice",
        "lut",
        "total"
    ]

    for line in lines:

        line_lower = line.lower()

        if "port of loading" in line_lower:

            # direct extraction
            match = re.search(
                r'port of loading\s*[:\-]?\s*([A-Za-z ()]+)',
                line,
                re.IGNORECASE
            )

            if match:

                value = match.group(1).strip()

                value = re.sub(
                    r'port of discharge.*',
                    '',
                    value,
                    flags=re.IGNORECASE
                ).strip()

                if (
                    len(value) > 4
                    and not any(
                        word in value.lower()
                        for word in ignore_words
                    )
                ):
                    return value

    # fallback
    known_ports = [
        "nhava sheva",
        "mundra",
        "mumbai",
        "chennai",
        "kandla"
    ]

    text = " ".join(lines).lower()

    for port in known_ports:
        if port in text:
            return port.title()

    return None

def extract_port_discharge(lines):

    ignore_words = [
        "delivery",
        "description",
        "invoice",
        "weight",
        "gross",
        "net",
        "lut",
        "total"
    ]

    for line in lines:

        line_lower = line.lower()

        if "port of discharge" in line_lower:

            match = re.search(
                r'port of discharge\s*[:\-]?\s*([A-Za-z ()]+)',
                line,
                re.IGNORECASE
            )

            if match:

                value = match.group(1).strip()

                value = re.sub(
                    r'place of delivery.*',
                    '',
                    value,
                    flags=re.IGNORECASE
                ).strip()

                if (
                    len(value) > 4
                    and not any(
                        word in value.lower()
                        for word in ignore_words
                    )
                ):
                    return value

    # fallback known destinations
    known_ports = [
        "constanta",
        "rotterdam",
        "hamburg",
        "singapore"
    ]

    text = " ".join(lines).lower()

    for port in known_ports:
        if port in text:
            return port.title()

    return None
def extract_pan(text):

    match = re.search(
        r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
        text,
        re.IGNORECASE
    )

    return match.group().upper() if match else None
def extract_package_count(text):

    match = re.search(
        r'(\d+)\s*(?:wooden\s*)?(?:box|boxes|package|packages)',
        text,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    return None
def extract_buyer_name(lines):

    patterns = [
        r'buyer.*?:?\s*(.+)',
        r'consignee.*?:?\s*(.+)',
        r'notify party.*?:?\s*(.+)'
    ]

    bad_words = [
        "invoice",
        "printed",
        "weight",
        "port",
        "checklist"
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if match:

                candidate = match.group(1).strip()

                if (
                    len(candidate) > 4
                    and not any(
                        w in candidate.lower()
                        for w in bad_words
                    )
                ):
                    return candidate

    return None
def extract_gstin(text):

    matches = re.findall(
        r'\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b',
        text,
        re.IGNORECASE
    )

    if matches:
        return matches[0].upper()

    # fallback PAN extraction
    pan_match = re.search(
        r'\b[A-Z]{5}\d{4}[A-Z]\b',
        text,
        re.IGNORECASE
    )

    if pan_match:
        return pan_match.group().upper()

    return None

def extract_total_amount(text):

    patterns = [
        r'total amt\.?\s*(?:in)?\s*eur\s*([0-9,.]+)',
        r'eur\s*([0-9,.]+)',
        r'total amount\s*[:\-]?\s*([0-9,.]+)'
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return normalize_amount(match.group(1))

    return None


def extract_gross_weight(text):
    match = re.search(
        r'gross weight.*?([0-9,.]+)\s*k',
        text,
        re.IGNORECASE | re.DOTALL
    )

    return normalize_amount(match.group(1)) if match else None


def extract_net_weight(text):
    match = re.search(
        r'net weight.*?([0-9,.]+)\s*k',
        text,
        re.IGNORECASE | re.DOTALL
    )

    return normalize_amount(match.group(1)) if match else None


# =========================
# COMPARISON
# =========================

def compare_invoice_fields(inv1, inv2):

    matching = {}
    different = {}

    essential_matches = 0

    for field in CRITICAL_FIELDS:

        value1 = inv1.get(field)
        value2 = inv2.get(field)

        if not value1 or not value2:
            continue

        score = similarity(str(value1), str(value2))

        is_match = False

        if field in [
            "invoice_number",
            "gst_vat_number"
        ]:
            is_match = score >= 0.90

        elif field in [
            "vendor_name",
            "buyer_name",
            "country_destination",
            "port_loading",
            "port_discharge"
        ]:

            is_match = (
                score >= 0.60
                or str(value1).lower() in str(value2).lower()
                or str(value2).lower() in str(value1).lower()
            )

        elif field in [
            "gross_weight",
            "net_weight",
            "total_amount"
        ]:
            is_match = compare_numeric(
                value1,
                value2
            )

        else:
            is_match = score >= 0.80

        payload = {
            "invoice1": value1,
            "invoice2": value2,
            "score": round(score * 100, 2)
        }

        if is_match:
            matching[field] = payload
            essential_matches += 1
        else:
            different[field] = payload

    same_invoice = essential_matches >= 5

    similarity_score = round(
        (
            len(matching)
            / len(CRITICAL_FIELDS)
        ) * 100,
        2
    )

    return {
        "same_invoice": same_invoice,
        "similarity_score": similarity_score,
        "matching_fields": matching,
        "different_fields": different,
    }


# =========================
# HELPERS
# =========================

def similarity(a, b):
    return SequenceMatcher(
        None,
        str(a).lower(),
        str(b).lower()
    ).ratio()


def compare_numeric(v1, v2):
    try:
        n1 = float(str(v1))
        n2 = float(str(v2))

        tolerance = max(n1, n2) * 0.02

        return abs(n1 - n2) <= tolerance

    except:
        return False


def normalize_amount(value):
    value = re.sub(r'[^0-9.]', '', str(value))

    try:
        return round(float(value), 2)
    except:
        return None


def normalize_text(text):
    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = ''.join(
        c for c in text
        if not unicodedata.combining(c)
    )

    text = re.sub(r'\s+', ' ', text)

    return text


def normalize_date(date_string):

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%b-%Y"
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(
                date_string,
                fmt
            )

            return parsed.strftime(
                "%Y-%m-%d"
            )
        except:
            pass

    return date_string
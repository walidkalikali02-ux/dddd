"""Import the leads list from CSV or Excel (Arabic or English column headers)."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from .db import Database

# Header aliases -> internal field name. Matching ignores case and spaces.
COLUMN_ALIASES = {
    "phone": ["phone", "mobile", "whatsapp", "number", "phone number", "رقم", "الرقم", "رقم الهاتف",
              "الهاتف", "موبايل", "الموبايل", "جوال", "الجوال", "واتساب", "رقم الواتساب"],
    "name": ["name", "contact", "contact name", "الاسم", "اسم", "اسم العميل", "العميل"],
    "business_name": ["business", "business name", "company", "brand", "store", "اسم النشاط", "النشاط",
                      "الشركة", "اسم الشركة", "المحل", "البراند"],
    "business_type": ["type", "category", "industry", "business type", "المجال", "نوع النشاط", "التصنيف", "القطاع"],
    "city": ["city", "location", "area", "المدينة", "المنطقة", "العنوان", "البلد"],
    "notes": ["notes", "note", "comment", "comments", "ملاحظات", "ملاحظة", "تفاصيل"],
    "source": ["source", "المصدر"],
}


def _norm(header: str) -> str:
    return re.sub(r"\s+", " ", str(header or "")).strip().lower()


def _map_headers(headers: list[str]) -> dict[int, str]:
    lookup = {_norm(alias): field for field, aliases in COLUMN_ALIASES.items() for alias in aliases}
    mapping = {}
    for index, header in enumerate(headers):
        field = lookup.get(_norm(header))
        if field and field not in mapping.values():
            mapping[index] = field
    return mapping


def normalize_phone(raw: str, default_country_code: str = "") -> str | None:
    """Return the number as international digits (e.g. '201001234567'), or None if it looks invalid."""
    if raw is None:
        return None
    text = str(raw).strip()
    # Excel sometimes turns numbers into floats like 201001234567.0
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    # Arabic-Indic digits -> ASCII
    text = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"))
    international = text.startswith("+") or text.startswith("00")
    digits = re.sub(r"\D", "", text)
    if digits.startswith("00"):
        digits = digits[2:]
    cc = re.sub(r"\D", "", default_country_code or "")
    if not international and cc:
        if digits.startswith("0"):
            digits = cc + digits.lstrip("0")
        elif not digits.startswith(cc):
            digits = cc + digits
    if not 8 <= len(digits) <= 15:
        return None
    return digits


def _read_rows(path: Path) -> tuple[list[str], list[list[str]]]:
    if path.suffix.lower() in {".xlsx", ".xlsm"}:
        from openpyxl import load_workbook

        sheet = load_workbook(path, read_only=True, data_only=True).active
        rows = [["" if c is None else str(c) for c in row] for row in sheet.iter_rows(values_only=True)]
    else:
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
    rows = [r for r in rows if any(cell.strip() for cell in r)]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def import_leads(path: str | Path, db: Database, default_country_code: str = "") -> dict:
    path = Path(path)
    headers, rows = _read_rows(path)
    mapping = _map_headers(headers)
    if "phone" not in mapping.values():
        raise ValueError(
            f"Couldn't find a phone column in {path.name}. Headers found: {headers}. "
            "Name the column 'phone' or 'رقم الهاتف'."
        )
    result = {"added": 0, "updated": 0, "skipped": [], "total": len(rows)}
    for line_no, row in enumerate(rows, start=2):
        record = {field: (row[i].strip() if i < len(row) else "") for i, field in mapping.items()}
        phone = normalize_phone(record.pop("phone"), default_country_code)
        if not phone:
            result["skipped"].append(line_no)
            continue
        if not record.get("source"):
            record["source"] = path.name
        _, created = db.upsert_lead(phone, **record)
        result["added" if created else "updated"] += 1
    return result

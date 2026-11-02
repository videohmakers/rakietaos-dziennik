#!/usr/bin/env python3
"""Eksport publicznej wersji Dziennika pokładowego rakietaOS.

Czyta zrzut bazy prywatnego dziennika (pliki JSON z ArtifactData, katalogi
entries/ i days/) i zapisuje data.json dla strony publicznej.

Zasady prywatności (od najważniejszej):
1. Dzień oznaczony private: true znika w całości, razem ze wszystkimi wpisami z tej daty.
2. Wpis oznaczony private: true znika.
3. Siatka bezpieczeństwa: jeśli w dniu albo wpisie pojawia się zastrzeżona fraza
   (BLOCKED poniżej), element znika, a skrypt to zgłasza.
4. Na stronę trafiają tylko pola z białej listy.

Użycie: python3 tools/export.py <katalog_zrzutu_bazy> <ścieżka_data.json>
Kod wyjścia 0 = OK. Ostrzeżenia idą na stderr.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BLOCKED = [r"rakieta\s+biznesu\s+live", r"\bRBL\b"]

ENTRY_FIELDS = ["date", "time", "what", "project", "meMin", "osMin", "baseMin", "meanwhile", "note"]
DAY_FIELDS = ["date", "dayNo", "title", "lead", "story", "turbulence", "idea",
              "stagesTitle", "stages", "beforeAfter", "inspiration"]


def load(dirpath):
    out = {}
    if dirpath.is_dir():
        for f in sorted(dirpath.glob("*.json")):
            out[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    return out


def has_blocked(obj):
    text = json.dumps(obj, ensure_ascii=False)
    return any(re.search(p, text, re.IGNORECASE) for p in BLOCKED)


def pick(obj, fields):
    return {k: obj[k] for k in fields if k in obj and obj[k] is not None}


def main(src, dst):
    src = Path(src)
    entries = load(src / "entries")
    days = load(src / "days")
    warnings = []

    private_dates = set()
    pub_days = {}
    for doc_id, d in days.items():
        date = d.get("date") or doc_id
        if d.get("private"):
            private_dates.add(date)
            continue
        if has_blocked(d):
            private_dates.add(date)
            warnings.append(f"Dzień {date} zawiera zastrzeżoną frazę, pominięty w całości.")
            continue
        pub_days[date] = pick(d, DAY_FIELDS)
        pub_days[date]["date"] = date

    pub_entries = []
    for doc_id, e in entries.items():
        date = e.get("date")
        if not date or e.get("private") or date in private_dates:
            continue
        if has_blocked(e):
            warnings.append(f"Wpis {doc_id} zawiera zastrzeżoną frazę, pominięty.")
            continue
        item = pick(e, ENTRY_FIELDS)
        item["id"] = doc_id
        pub_entries.append(item)

    data = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "days": pub_days,
        "entries": pub_entries,
    }
    Path(dst).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    for w in warnings:
        print("UWAGA:", w, file=sys.stderr)
    print(f"Zapisano {dst}: {len(pub_days)} dni, {len(pub_entries)} wpisów publicznych; "
          f"pominięte prywatne daty: {sorted(private_dates) or 'brak'}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])

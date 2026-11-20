"""Validates app/src/main/res/raw/watchface.xml against the vendored official WFF v2 XSD.

Run: python tools/validate_wff.py     (needs: pip install xmlschema)
Exit code 0 = valid. Also runs a negative test to prove the validator really rejects bad input.
"""
import sys
from pathlib import Path

import xmlschema

ROOT = Path(__file__).resolve().parent.parent
XSD = ROOT / "tools" / "wff-schema" / "v2" / "watchface.xsd"
XML = ROOT / "app" / "src" / "main" / "res" / "raw" / "watchface.xml"

schema = xmlschema.XMLSchema11(str(XSD))
errors = list(schema.iter_errors(str(XML)))
print("errors:", len(errors))
for e in errors[:5]:
    print(str(e)[:900])
    print("---")

bad = XML.read_text(encoding="utf-8").replace("<DigitalClock ", '<DigitalClock bogus="1" ', 1)
neg = len(list(schema.iter_errors(bad)))
print("negative test errors (expect > 0):", neg)

sys.exit(1 if errors or neg == 0 else 0)

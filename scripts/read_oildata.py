import os
import csv
from pydantic import BaseModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class OilData(BaseModel):
    wellbore: str
    doc_type: str
    doc_name: str
    doc_url: str
    doc_format: str
    doc_size: str
    NPDID: str
    date_updated: str
    date_synced: str

    class Config:
        # Allow extra fields to be ignored if present
        extra = "ignore"


def read_oildata(path: str) -> list[OilData]:
    ret = []
    with open(path) as file:
        rdr = csv.reader(file, delimiter=";", quotechar='"')
        first = True
        for r in rdr:
            if first or len(r) == 0:
                first = False
                continue

            oil_entry = OilData(
                wellbore=r[0],
                doc_type=r[1],
                doc_name=r[2],
                doc_url=r[3],
                doc_format=r[4],
                doc_size=r[5],
                NPDID=r[6],
                date_updated=r[7],
                date_synced=r[8],
            )
            ret.append(oil_entry)
    return ret


if __name__ == "__main__":
    entries = read_oildata(os.path.join(CURRENT_DIR, "../data/oildata.csv"))

    # Example of filtering the csv
    for entry in entries:
        if (
            "COMPLETION" in entry.doc_name.upper()
            and "REPORT" in entry.doc_name.upper()
            and "LOG" not in entry.doc_name.upper()
        ):
            print(entry.doc_name)

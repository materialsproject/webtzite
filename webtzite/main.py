import re
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class MDB:
    cmp_tbl = {">": "$gt", ">=": "$gte", "<": "$lt", "<=": "$lte", "==": "$eq", "!=": "$ne"}

    def __init__(self):
        from mongogrant import Client
        self.client = Client()
        self.core_db = self.client.db("ro:dev/optimade_core")

    def get_structure(self, structure_id):
        doc = self.core_db.materials.find_one({"task_id": structure_id})
        if doc:
            return Structure.from_material_doc(doc)

    def get_structures(self, filter_):
        match = re.search(r'nelements([^0-9]+)([0-9]+)', filter_)
        if match:
            comp, n = match.groups()
            crit = {"nelements": {self.cmp_tbl[comp]: int(n)}}
            return [Structure.from_material_doc(doc) for doc in
                    mdb.core_db.materials.find(crit, Structure.material_doc_projection())]
        else:
            return []


mdb = MDB()


class Entry(BaseModel):
    id: str
    modification_date: str


class Structure(Entry):
    elements: str
    nelements: int
    chemical_formula: str
    formula_prototype: str
    _mp_cif: str

    @staticmethod
    def from_material_doc(doc):
        return Structure(**{
            "id": doc["task_id"],
            "modification_date": doc["last_updated"].isoformat(),
            "elements": ",".join(doc["elements"]),
            "nelements": doc["nelements"],
            "chemical_formula": doc["pretty_formula"],
            "formula_prototype": doc["formula_anonymous"],
            "cif": doc["cif"],
        })

    @staticmethod
    def material_doc_projection():
        return ["task_id", "last_updated", "elements", "nelements", "pretty_formula", "formula_anonymous", "cif"]


@app.get("/")
def get_home():
    return {"hello": "world"}

@app.get("/structures", response_model=List[Structure])
def get_structures(filter_: str):
    return [out.dict() for out in mdb.get_structures(filter_)]


@app.get("/structures/{structure_id}", response_model=Structure)
def get_structure(structure_id: str) -> Structure:
    return mdb.get_structure(structure_id).dict()


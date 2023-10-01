
import json

class RestAPI:
    def __init__(self, database=None):
        self.database = database if database else {"users": []}

    def get(self, url, payload=None):
        if url == "/users":
            if payload:
                names = json.loads(payload)["users"]
                return json.dumps({"users": [user for user in self.database["users"] if user["name"] in names]})
            else:
                return json.dumps(self.database)

    def post(self, url, payload=None):
        if url == "/add":
            name = json.loads(payload)["user"]
            self.database["users"].append({
                "name": name,
                "owes": {},
                "owed_by": {},
                "balance": 0.0
            })
            return json.dumps(self.database["users"][-1])
        elif url == "/iou":
            data = json.loads(payload)
            lender, borrower, amount = data["lender"], data["borrower"], data["amount"]
            for user in self.database["users"]:
                if user["name"] == lender:
                    user["owed_by"][borrower] = user["owed_by"].get(borrower, 0) + amount
                    user["balance"] += amount
                elif user["name"] == borrower:
                    user["owes"][lender] = user["owes"].get(lender, 0) + amount
                    user["balance"] -= amount
            return json.dumps({"users": sorted([user for user in self.database["users"] if user["name"] in [lender, borrower]], key=lambda x: x["name"])})

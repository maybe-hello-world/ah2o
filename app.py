from fastapi import FastAPI, Request, HTTPException, status
import uvicorn
import os
import asyncio
from os import path
import logging
import frontmatter

# shared secret key for authentication
SECRET_KEY = os.getenv("AH2O_SECRET_KEY")
if not SECRET_KEY:
    raise Exception("Secret key not configured")

# location of Obsidian daily notes
DAILY_NOTES_LOCATION = os.getenv("AH2O_DAILY_NOTES_LOCATION")
if not DAILY_NOTES_LOCATION:
    raise Exception("Daily notes location not configured")

# Convert lb to kg by default
CONVERT_LB_TO_KG = os.getenv("AH2O_CONVERT_LB_TO_KG", "true").lower() == "true"

app = FastAPI()


@app.get("/health")
async def health():
    return {"message": "Healthy!"}


@app.post("/healthmetrics")
async def save_json_to_file(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header != SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    json_data = await request.json()
    asyncio.create_task(parse_metrics(json_data))
    return {"message": "Success"}


def lb_to_kg(lb):
    return lb * 0.453592


def date_to_path(date: str):
    filename = date.split(" ")[0] + ".md"
    return path.join(DAILY_NOTES_LOCATION, filename)


def save_to_frontmatter(note_path: str, key: str, value: str, units: str):
    if not path.exists(note_path):
        open(note_path, "w").close()

    post = frontmatter.load(note_path)
    post[key] = f"{value} {units}"
    with open(note_path, "w") as f:
        f.write(frontmatter.dumps(post))


def parse_and_save(metric: dict):
    # example:
    # {
    #     "name": "basal_energy_burned",
    #     "units": "kcal",
    #     "data": [
    #         {
    #             "source": "",
    #             "date": "2024-09-20 00:00:00 -0700",
    #             "qty": 1420.710739391346
    #         },
    #         {
    #             "date": "2024-09-21 00:00:00 -0700",
    #             "source": "",
    #             "qty": 1428.6691966059852
    #         },
    #         {
    #             "qty": 749.7120640026696,
    #             "date": "2024-09-22 00:00:00 -0700",
    #             "source": ""
    #         }
    #     ]
    # },

    if ("name" not in metric) or ("units" not in metric) or ("data" not in metric):
        logging.error(f"Invalid metric: {metric}")
        return

    name = metric["name"]
    units = metric["units"]
    data = metric["data"]

    for value in data:
        if "date" not in value or "qty" not in value:
            logging.error(f"Invalid value: {value}")
            continue

        qty = value["qty"]
        date = date_to_path(value["date"])

        converted_units = units
        if units == "lb" and CONVERT_LB_TO_KG:
            qty = lb_to_kg(qty)
            converted_units = "kg"

        save_to_frontmatter(date, name, qty, converted_units)


async def parse_metrics(data: dict):
    metrics = data.get("data", {}).get("metrics", [])
    if not metrics:
        logging.error("No metrics found in the data")
        logging.debug(data)
        return

    for metric in metrics:
        try:
            parse_and_save(metric)
        except Exception as e:
            logging.error(f"Error parsing metric: {metric}")
            logging.error(e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

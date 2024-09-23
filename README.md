# ah2o
Apple Health 2 Obsidian

## Description

This is a simple REST API to get Apple Health data and write it down to daily notes of Obsidian. I use [Health Auto Export](https://apps.apple.com/us/app/health-auto-export-json-csv/id1115567069) app to export data from Apple Health and push it to this API which then writes it down to daily notes in Obsidian. Obsidian vault is accessible on the server where this API is running (in my case - via OneDrive).

I implemented this just because I want to store this data in Obsidian. Unfortunately, Health Auto Export app is paid (6$/year), but it's easier than doing it manually. If you know how to do it manually or can implement it and put to Open Source, please tell me and I'll be happy to use it.

## Installation

Run the Docker container:
    
```bash
docker run -d -p 8000:8000 --name ah2o --restart=always -e AH2O_SECRET_KEY=<unique secret key> -e AH2O_DAILY_NOTES_LOCATION=/daily_notes -e AH2O_CONVERT_LB_TO_KG=true -v /path/to/vault/daily_notes:/daily_notes maybehelloworld/ah2o
```

AH2O_SECRET_KEY - unique secret key to authorize requests, just create a random string  
AH2O_DAILY_NOTES_LOCATION - location of daily notes in Obsidian vault connected (on your filesystem)
AH2O_CONVERT_LB_TO_KG - convert weight from lb to kg (true/false)


Install Health Auto Export app and configure it to export data to `http://<your-ip>:8000/healthmetrics` in JSON format. Add header `Authorization` with your `<unique secret key>`. Please use daily aggregation of metrics during export. You can set automation to export data periodically.

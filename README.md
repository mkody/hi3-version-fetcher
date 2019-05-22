# Fetch servers version for HI3

## Required
- Python 3
- A markdown document with `<!-- VER -->` and `<!-- /VER -->` tags to mark where the table will be.  
  Also edit the `fetch.py` with the correct path to your doc (the first `open()` in the code).


## Setup
```bash
pip3 install pytz
cp hi3s.json.dist hi3s.json
$EDITOR hi3s.json
```

Edit the `version` key for each server to match the current version, 
as this file might get largely outdated.


## Run
Run a cron at least once every day. Don't run too frequently tho.

`python3 fetch.py > cron.log 2>&1` 


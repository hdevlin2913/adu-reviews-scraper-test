# ADU-REVIEWS-SCRAPER

## How to run

### Manually

1. Install

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create a input `./storage/key_value_stores/default/INPUT.json` file

```json
{
   "type": "",
   "params": {
       "query": [],
       "max_places_page": null,
       "max_reviews_page": null
   },
   "useApifyProxy": false
}
```

> **_NOTE:_** Fill in the type, query, max_places_page and max_reviews_page as you like. <br/>
> type in ["attractions", "restaurants", "hotels"]

3. Run the Actor

```sh
python3 -m src
```

### Using Makefile

1. Create an INPUT.json file and start the Actor

```sh
make seed_input
make start
```

2. Check logs

```sh
make logs [service name, default is all]
```

## Pre-commit

```sh
pre-commit run --all-files
```

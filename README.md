# ADU Reviews Scraper

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/True-Digital-Vietnam/adu-reviews-scraper.git
   cd adu-reviews-scraper
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

   or

   ```bash
   poetry update
   ```

3. Activate the virtual environment:

   ```bash
   poetry shell
   ```

## Usage

### Makefile Run

You can also use the provided Makefile to run the scraper. The Makefile includes predefined commands for convenience:

```bash
make install start
```

Available commands:

-  `scrape reviews`: to scrape data from Tripadvisor

## Results

The scraped data will be saved in the `storage/` folder. You can find the exported files in this directory after running the scraper.

# Open Food Facts Scraper

This project is a web scraper developed in Python to extract product information from the [Open Food Facts](https://es.openfoodfacts.org) website. It uses Selenium and BeautifulSoup to navigate pages and collect data such as:

- Product name
- Brand
- Ingredients
- Allergens
- Nutritional information

The scraped data is saved in a CSV file, and any errors are logged.

## Project Structure

```
scraping/
├── core/
│   ├── config.py      # Global configuration (limits, URLs, paths, etc.)
│   ├── scraper.py     # Main scraping logic
│   └── utils.py       # Helper functions (logging, cleaning, etc.)
├── output/
│   ├── scraped_products.csv
│   └── errores.log
├── main.py            # Project entry point
```

## Requirements

- Python 3.7 or higher
- [Selenium](https://pypi.org/project/selenium/)
- [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)
- [webdriver-manager](https://pypi.org/project/webdriver-manager/)

## Configuration

The core/config.py file contains the global configurations, including:

- Selenium Options: Headless mode, user-agent, etc.

- Scraping Parameters: Limits for categories, pages, and products.

- URLs and Output Paths: Base URL, categories URL, CSV and log file names.

- These parameters according to specifict needs.

## Usage

To run the scraper, simply execute the main.py file:

`python main.py`

During execution, the scraper will perform the following tasks:

- Category Retrieval: Navigates to the main page to extract available categories.

- Category and Product Processing: Iterates through each category, processes pages, and extracts product information.

- Output Generation: Saves the scraped data into scraped_products.csv and logs any errors into errores.log.

## Additional Notes

- Headless Mode: The scraper runs in headless mode by default. To view the browser's actions, modify the options in core/config.py.

- Testing Limits: The limits for categories, pages, and products are set for testing. Adjust these values in the configuration file if you require more data.

- Google Chrome: Ensure that Google Chrome is installed on your system, as it is used for Selenium navigation.

## License

This project is licensed under the ODbL License. See the LICENSE file for more details.





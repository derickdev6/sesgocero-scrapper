# Sesgocero Scrapper

A Scrapy-based web scraper that collects news articles from major Colombian news websites.

## Supported News Sources

- El Tiempo
- El País
- El Espectador

## Features

- Automated news article collection
- Unique article identification to prevent duplicates
- Structured data extraction including:
  - Article ID
  - Title
  - Subtitle
  - Publication Date
  - Content
  - URL
  - Source

## Prerequisites

- Python 3.x
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sesgocero-scrapper.git
cd sesgocero-scrapper
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Running All Spiders

To run all spiders at once:
```bash
cd sesgocero_scrapper
scrapy list | xargs -n 1 scrapy crawl
```

### Running Individual Spiders

To run a specific spider:
```bash
scrapy crawl el_tiempo
scrapy crawl el_pais
scrapy crawl el_espectador
```

### Output

The scraped data will be saved according to your configured pipeline settings. Make sure to configure your database or storage settings in `settings.py` before running the spiders.

## Project Structure

```
sesgocero_scrapper/
├── scrapy.cfg
├── requirements.txt
└── sesgocero_scrapper/
    ├── __init__.py
    ├── items.py
    ├── middlewares.py
    ├── pipelines.py
    ├── settings.py
    └── spiders/
        ├── __init__.py
        ├── el_tiempo.py
        ├── el_pais.py
        └── el_espectador.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Scrapy](https://scrapy.org/)
- Thanks to all contributors who have helped shape this project 
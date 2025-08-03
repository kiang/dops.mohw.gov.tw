#!/usr/bin/env python3
from crawler import TaiwanOpenDataCrawler

# Test with just one dataset
crawler = TaiwanOpenDataCrawler()
crawler.process_dataset('152223')
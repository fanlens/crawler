#!/bin/bash
scrapy crawl $1 -a source_id=$2 -a since=-30 -a api_key=$3

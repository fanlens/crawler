#!/bin/bash
. ../../fanlens-venv-intel/bin/activate
scrapy crawl $1 -a source_id=$2 -a since=-14 -a api_key=WyI1IiwiYzE2YjRlMTBjMjE1MGI0YzM0ZWE4MWRiNDUxNTg2OWIiXQ.C5lyMQ.jxdiXrk68Iww8oAS_1PBF4QtFQw
deactivate

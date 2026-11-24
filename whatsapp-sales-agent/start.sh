#!/usr/bin/env bash
cd "$(dirname "$0")"
python3 -m sales_agent serve "$@"

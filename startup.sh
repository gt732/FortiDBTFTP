#!/bin/bash

# Run Python script to create table
python create_table.py

# Run py3tftp with specified options
py3tftpsql --host 0.0.0.0 -p 69

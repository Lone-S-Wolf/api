<!-- PURGING CACHE FILE -->

find . -name "\*.pyc" -delete
find . -name "**pycache**" -type d -exec rm -r {} +

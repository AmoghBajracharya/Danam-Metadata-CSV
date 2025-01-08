To be updated...

# Using scripts directly
Clean DANAM JSON:
python clean_json.py -f json\DANAM\<JSON dump>

Create CSV file:
python write_csv.py -f json/cleaned-metadata/image_<TIME>.json -report -ids id_monument.txt

Download missing images from DANAM:
python download_danam.py -f <list of missing images>



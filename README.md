# Stenography-tool
#Code for unit testing
python -m unittest discover tests

#Unit testing one by one
python -m unittest tests/test_image.py


#CLI code for encoding
python3 cli.py image --encode --input tests/test_image.png --output encoded_image.png --message "Hello World"

#CLI code for decoding
python cli.py image --decode --input encoded_image.png

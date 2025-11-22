cd src
echo "Cloning DotsOCR... in $PWD"
git clone https://github.com/rednote-hilab/dots.ocr.git
cd dots.ocr

echo "Installing DotsOCR weights... to $PWD/dots.ocr"
pip install -e .
python3 tools/download_model.py

cd ..
mkdir -p weights/DotsOCR
cp -r dots.ocr/weights/DotsOCR weights/DotsOCR
rm -rf dots.ocr

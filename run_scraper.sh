cd utils
python api_scraper_cattles.py
cd ../
git add .
git commit -m 'New datapoint added'
git push origin main
python -m utils.dataset_generator
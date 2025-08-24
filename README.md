# Cow-weight-and-Breed-Prediction

## Overleaf

1. [Draft](https://www.overleaf.com/read/pvdhwqhqptfm)

## Plans

1. [Session 4](https://github.com/bhuiyanmobasshir94/NUS-Artificial-Intelligence-Training/tree/main/Sessions/SESSION_4)
2. [Session 5](https://github.com/bhuiyanmobasshir94/NUS-Artificial-Intelligence-Training/tree/main/Sessions/SESSION_5)

## Scraper With Puppeteer

1. [A Guide to Web Scraping With JavaScript and Node.js](https://hackernoon.com/a-guide-to-web-scraping-with-javascript-and-nodejs-i21l3te1)
2. [puppeteer](https://github.com/puppeteer/puppeteer)
3. [puppeteer-cluster](https://github.com/thomasdondorf/puppeteer-cluster)
4. [Web Scraping with a Headless Browser: A Puppeteer Tutorial](https://www.toptal.com/puppeteer/headless-browser-puppeteer-tutorial)
5. [Saving and scraping a website with Puppeteer](https://fettblog.eu/scraping-with-puppeteer/)

## SQLite with SQLAlchemy

1. [Storing a Python dict as JSON in SQLite using SQLAlchemy](https://blog.stigok.com/2020/09/06/sqlalchemy-sqlite-json-column-field.html)
2. [Data Management With Python, SQLite, and SQLAlchemy](https://realpython.com/python-sqlite-sqlalchemy/)

## Video Classification Resources

1. [How to use the Keras Functional API for Deep Learning](https://machinelearningmastery.com/keras-functional-api-deep-learning/)
2. [Multi-input Multi-output Model with Keras Functional API](https://stackoverflow.com/questions/66845924/multi-input-multi-output-model-with-keras-functional-api)
3. [Video classification with Keras and Deep Learning - PyImageSearch](https://www.pyimagesearch.com/2019/07/15/video-classification-with-keras-and-deep-learning/)
4. [Keras: Multiple Inputs and Mixed Data - PyImageSearch](https://www.pyimagesearch.com/2019/02/04/keras-multiple-inputs-and-mixed-data/)
5. [alxcnwy/Deep-Neural-Networks-for-Video-Classification](https://github.com/alxcnwy/Deep-Neural-Networks-for-Video-Classification)
6. [Introduction to Video Classification and Human Activity Recognition](https://learnopencv.com/introduction-to-video-classification-and-human-activity-recognition/)
7. [Keras: Multiple outputs and multiple losses](https://www.pyimagesearch.com/2018/06/04/keras-multiple-outputs-and-multiple-losses/)
8. [3 ways to create a Keras model with TensorFlow 2.0 (Sequential, Functional, and Model Subclassing)](https://www.pyimagesearch.com/2019/10/28/3-ways-to-create-a-keras-model-with-tensorflow-2-0-sequential-functional-and-model-subclassing/)
9. [Understanding Embedding Layer in Keras](https://medium.com/analytics-vidhya/understanding-embedding-layer-in-keras-bbe3ff1327ce)
10. [Deep Learning for Tabular Data using PyTorch](https://towardsdatascience.com/deep-learning-for-tabular-data-using-pytorch-1807f2858320)

## Video data loading

1. [Video-Dataset-Loading-Pytorch](https://github.com/RaivoKoot/Video-Dataset-Loading-Pytorch)

## Dataset Publish Ideas

1. [~](https://www.researchgate.net/deref/https%3A%2F%2Fwww.mdpi.com%2Fjournal%2Fdata)
2. [~](https://www.researchgate.net/deref/https%3A%2F%2Fwww.journals.elsevier.com%2Fdata-in-brief)

## Curated List

1. [Write your own Custom Data Generator for TensorFlow Keras](https://medium.com/analytics-vidhya/write-your-own-custom-data-generator-for-tensorflow-keras-1252b64e41c3)
2. [Stackoverflow thread](https://stackoverflow.com/a/25421946/7195890)

## Bengalmeat public API

Please take you permissions from the proper authority before using this

```
https://admin.bengalmeat.com/api/cattle/
```

```
https://admin.bengalmeat.com/api/cattle/{{CATTLE_ID}}/detail
```

N.B: All the scraped images and data are from Bengalmeat's public-facing website.

## AWS Query

```
aws s3 ls --recursive s3://{AWS_BUCKET_NAME}/images/ --human-readable --summarize
aws s3 ls --recursive s3://{AWS_BUCKET_NAME}/videos/ --human-readable --summarize
```

## AWS S3 Sync notes

Command:
AWS_PROFILE=cli-algorec ./s3_transfer_optimized.sh -b cid-mbs -p cow-data -t 15 &

Explanation:
This command runs the s3_transfer_optimized.sh script to sync files to the S3 bucket named 'cid-mbs' from the local directory 'cow-data'. The '-t 15' option sets the number of parallel threads to 15 for faster uploads. The '&' at the end runs the command in the background, allowing you to continue using the terminal.

Important Notes:

```
  1. Ensure AWS CLI is configured with the profile 'cli-algorec'.
  2. The script uses 'aws s3 sync' which only uploads new or changed files.
  3. Monitor progress with 'tail -f transfer.log' if using nohup.
```

Existing Files:
No, it won't re-upload existing files! AWS S3 sync is smart - it only uploads files that don't exist or have changed. It compares file sizes and modification times.

    Sleep Mode Issue: Running with & won't survive sleep mode on macOS. The process will pause when your Mac sleeps.

    Better Solutions:

    Option 1: Prevent sleep during transfer:
    # Keep Mac awake during transfer
    caffeinate -s AWS_PROFILE=cli-algorec ./s3_transfer_optimized.sh -b cid-mbs -p cow-data -t 15

    Option 2: Use nohup for background resilience:
    # Run in background, immune to hangups
    nohup AWS_PROFILE=cli-algorec ./s3_transfer_optimized.sh -b cid-mbs -p cow-data -t 15 > transfer.log 2>&1 &

    # Check progress anytime with:
    tail -f transfer.log

    Option 3: Use tmux/screen (best for long transfers):
    # Install tmux if needed: brew install tmux
    tmux new-session -d -s s3transfer
    tmux send-keys -t s3transfer 'AWS_PROFILE=cli-algorec ./s3_transfer_optimized.sh -b cid-mbs -p cow-data -t 15' Enter

    # Detach and let it run: Ctrl+B, then D
    # Reattach anytime: tmux attach -t s3transfer

    Recommendation: Use caffeinate for simplest approach, or tmux if you want to detach/reattach to monitor progress.

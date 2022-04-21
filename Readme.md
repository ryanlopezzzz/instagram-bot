# Instagram Bot - UCSB Data Science Club Project

This repository does the following:
* Automated data collection on Instagram users and posts.
* Automated actions on Instagram, such as following, liking, commenting, posting, and sending DMs.

## Installation:
After cloning this repository with git, it is recommended to use Anaconda and create an insta_bot_env environment. This can be done with the following command in the *instagram_api* directory:

`conda env create -f insta_bot_env.yml`

Here are the (non-standard) packages used:
* Ping's Instagram API for data collection: [Github](https://github.com/ping/instagram_private_api) | [Documentation](https://instagram-private-api.readthedocs.io/en/latest/api.html#module-instagram_private_api)
* Instauto API for posting photos: [Github](https://github.com/stanvanrooy/instauto) | [Documentation](https://instauto.readthedocs.io/en/latest/)
* Names for generating random names: [Names Package](https://pypi.org/project/names/)
* Pyclick for making human-like mouse movements: [Pyclick Package](https://pypi.org/project/pyclick/)
* Pynput for automated typing on keyboard: [Pynput Package](https://pypi.org/project/pynput/)
* OpenCV for computer vision: [OpenCV Package](https://pypi.org/project/opencv-python/)
* PyTesseract for text detection: [PyTesseract Package](https://pypi.org/project/pytesseract/)

## Data Collection:
The official Instagram API does not allow you to collect data on other users. Luckily, [Ping's API](https://github.com/ping/instagram_private_api) has a work around by creating Samsung phone headers and requesting from the old API endpoints.

We wrote code to safely call Ping's API and organize the data collected into Pandas dataframes. See [this notebook](notebooks/tutorial_using_data_tables.ipynb) for how to load and play around with the data.

## Instagram Bot Automation:
The typical Python approach of using selenium-stealth or undetected chrome driver to automate interactions (liking, commenting, etc.) quickly result in account bans. To get past this issue, we use computer vision to identify the location of buttons and use human-like mouse movements to navigate the webpage. This way we don't interact with the webpage in a non-human way. For the computer vision, a lot of parameters were tweaked for my personal computer, so you may need to change them.
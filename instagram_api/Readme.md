# Instagram Bot
This repository does the following:
* Automated data collection on Instagram users and posts.
* Performs statistics on this data.
* Automated actions on Instagram, such as following, liking, commenting, and posting.

## Installation:
After cloning this repository with git, it is recommended to use Anaconda and create an insta_bot_env environment. This can be done with the following command in the *instagram_api* directory:

`conda env create -f insta_bot_env.yml`

Here are the (non-standard) packages used:
* Ping's Instagram API for data collection: [Github](https://github.com/ping/instagram_private_api) | [Documentation](https://instagram-private-api.readthedocs.io/en/latest/api.html#module-instagram_private_api)
* Instauto API for posting photos: [Github](https://github.com/stanvanrooy/instauto) | [Documentation](https://instauto.readthedocs.io/en/latest/)
* Names for generating random names: [Names Package](https://pypi.org/project/names/)
* Pyclick for making human-like mouse movements: [Pyclick Package](https://pypi.org/project/pyclick/)
* Pynput for automated typing on keyboard: [Pynput Package](https://pypi.org/project/pynput/)
* [Orjson](https://pypi.org/project/orjson/1.3.0/) 


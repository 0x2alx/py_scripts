# tweepy-opensea-sales-bot
 
<!-- PROJECT SHIELDS -->
<!--
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![MIT License][license-shield]][license-url]
<!--[![LinkedIn][linkedin-shield]][linkedin-url]-->



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <!--<a href="https://github.com/ncvanegmond/tweet_opensea_sale_bot">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>-->

  <h3 align="center">OpenSea Tweet BOT</h3>

  <p align="center">
    Simple Tweepy bot that tweets out the most recent sale on OpenSea for a specific collection
    <br />
    <a href="https://github.com/ghooost0x2a/py_scripts/tree/opensea_tweet_bot"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ncvanegmond/tweet_opensea_sale_bot">OG Code</a>
    ·
    <a href="https://twitter.com/avril15sales">View Demo</a>
    ·
    <a href="https://github.com/ghooost0x2a/py_scripts/issues">Report Bug</a>
    ·
    <a href="https://github.com/ghooost0x2a/py_scripts/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <!--<li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>-->
    <li><a href="#changes">Changes from OG code</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Simple tweepy bot that will periodically call the Opensea API to check if there are new sales for a specific collection and tweets about it. This bot is based on the code here: https://github.com/ncvanegmond/tweet_opensea_sale_bot

Requires OpenSea API KEY. 

You can see it in action at [@avril15sales](https://twitter.com/avril15sales)

### Built With

* [Tweepy](https://www.tweepy.org/)
* [Opensea API](https://docs.opensea.io/reference/api-overview)




<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Installation

1. Read the docs on the [Opensea API](https://docs.opensea.io/reference/api-overview)
2. Clone the repo
   ```sh
   git clone https://github.com/ghooost0x2a/py_scripts.git
   ```
   ```sh
   git checkout opensea_tweet_bot
   ```   
3. Install packages
   ```sh
   pip install -r requirements.txt
   ```
4. Enter your Twitter API keys and OpenSea parameters in `.env`
   ```sh
   # Twitter keys
   API_KEY = xxx
   API_SECRET = xxx
   ACCESS_TOKEN = xxx
   ACCESS_TOKEN_SECRET = xxx
   # OpenSea collection parameters
   COLLECTION_SLUG = avril15s01
   CONTRACT_ADDRESS = 0xf94c7c60732979e8e24c75883fc8df66158c5fed
   OS_API_KEY = xxx
   ```
<!-- CHANGES -->
## Changes from OG code

Distributed under the MIT License. See `LICENSE` for more information.


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Alex - [@ghooost0x2a](https://twitter.com/ghooost0x2a)

Project Link: [https://github.com/ghooost0x2a/py_scripts/tree/opensea_tweet_bot](https://github.com/ghooost0x2a/py_scripts/tree/opensea_tweet_bot)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Niels van Egmond for the orignal code](https://github.com/ncvanegmond/tweet_opensea_sale_bot)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ncvanegmond/tweet_opensea_sale_bot.svg?style=for-the-badge
[contributors-url]: https://github.com/ghooost0x2a
[forks-shield]: https://img.shields.io/github/forks/ncvanegmond/tweet_opensea_sale_bot.svg?style=for-the-badge
[forks-url]: https://github.com/ncvanegmond/tweet_opensea_sale_bot/network/members
[stars-shield]: https://img.shields.io/github/stars/ncvanegmond/tweet_opensea_sale_bot.svg?style=for-the-badge
[stars-url]: https://github.com/ncvanegmond/tweet_opensea_sale_bot/stargazers
[issues-shield]: https://img.shields.io/github/issues/ncvanegmond/tweet_opensea_sale_bot.svg?style=for-the-badge
[issues-url]: https://github.com/ncvanegmond/tweet_opensea_sale_bot/issues
[license-shield]: https://img.shields.io/github/license/ncvanegmond/tweet_opensea_sale_bot.svg?style=for-the-badge
[license-url]: https://github.com/ncvanegmond/tweet_opensea_sale_bot/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
# WhatsApp Web Data Extraction Tool
A set of Python program that extracts chat data from WhatsApp Web and display an overview of it

## Installation and Usage
### Requirement
* Python 3.10.9 ([Setup Python](https://www.python.org/downloads/release/python-3109/))
* spaCy - English ([Setup spaCy](https://spacy.io/usage))
* Matplotlib - Graph ([Setup Matplotlib](https://matplotlib.org/stable/install/index.html))
* Selenium ([Setup Selenium](https://pypi.org/project/selenium/))

### How-to-use
<ol>
  <li>Run main.py</li>
  <li>Follow the instruction on the page popped up and link your device</li>
  <li>Wait for the process to finish</li>
  <li>Navigate the overview of the chat data in the GUI</li>
</ol>

## Tools
<ul>
  <li>Python</li>
  <li>Selenium</li>
  <li>Tkinter (GUI)</li>
  <li>spaCy (NER)</li>
  <li>SQLite (Built-in database)</li>
</ul>

## Specification
### Media Download Supported
The tool supports downloading text messages, images and videos

### Anonymisation
The tool will anonymise the following sensitive information by recognising certain patterns
* Email addresses<br>
  ![Mask Email](https://imgur.com/4Lzu29F.png)
* UK Phone numbers<br>
  ![Mask Phone numbers](https://imgur.com/9WDO6QI.png)
* 16-digit card numbers<br>
  ![Mask Phone numbers](https://imgur.com/B5rFz65.png)

### Overview
* Number of <b><i>messages</i></b> sent by each party in a chat
* Number of <b><i>images</i></b> sent by each party in a chat
* Number of <b><i>videos</i></b> sent by each party in a chat
* Number of messages sent <b><i>GROUPED BY</i></b> date
  ![GUI Demo](https://imgur.com/55WEsoF.png)

## Demo


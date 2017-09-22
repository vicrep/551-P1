#import praw
import json
import mistune
#import nltk
#from nltk.corpus import stopwords
from langdetect import detect
import xml.etree.cElementTree as ET

# Define a Renderer for the Markdown parser
# The default Renderer convert Markdown to html, we don't need HTML so we define our own rules
class PureTextRenderer(mistune.Renderer):
    def emphasis(self, text):
        return text

    def double_emphasis(self, text):
        return text

    def link(self, link, title, text):
        return '%s (%s)' % (text, link)

    def paragraph(self, text):
        return text

    def header(self, text, level, raw=None):
        return ''

    def list_item(self, text):
        return '%s, ' % (text)

    def strikethrough(self, text):
        return text

    def list(self, body, ordered=True):
        return body

    def block_quote(self, text):
        return ' "%s" ' % (text)

    def linebreak(self):
        return ' \n'

renderer = PureTextRenderer()
markdown = mistune.Markdown(renderer=renderer)
#nltk.download('stopwords')

maxId = 0
nbOfDialogs = 0
users = dict()

def cleanText( s ):

    s = markdown(s)
    # Removing end of lists followed by point (ex: "a, b, c, .")
    s = s.replace(', .', '.')
    s = s.replace(', \n', '.')
    s = s.replace(',\n', '.')

    s = s.replace('\n', ' ')
    s = s.replace('\t', ' ')

    s = s.lower()

    # Removing stopwords
    # Multiple spaces are removed at the same time
    #s = ' '.join([word for word in s.split() if not word in stopwords.words('french')])
 
    # Removing sarcasm tag
    s = s.replace ('/s', '')
    return s

def createXML():
    root = ET.Element("dialog")
    return root

def createDialog(root):
    dialog = ET.SubElement(root, "s")
    return dialog

def addEntryToDialog(dialog, text, user):
    if(user not in users):
        global maxId
        maxId = maxId + 1
        users[user] = maxId
    u = '%i' % users[user]

    ET.SubElement(dialog, "utt", uid=u).text = text

# Creates a dialog using a list extracted from a tree
def createDialogFromList(root, l):
    global nbOfDialogs
    nbOfDialogs = nbOfDialogs + 1

    dialog = createDialog(root)
    for message in l:
        user = ""
        text = ""
        if("comments" in message): # Is it the first post?
            if(message["text"] != ""):
                text = message["text"]
            else:
                text = message["title"]
        else:
            user = message["author_name"]
            text = message["body"]

        addEntryToDialog(dialog, cleanText(text), user)

def saveXML(root, outputfile):
    tree = ET.ElementTree(root)
    tree.write(outputfile)

# Depth First Search
def DFS(root, current, l):
    # Detecting the language
    lang = 'fr'
    tag = 'title'
    if("title" in current):
        tag = 'title'
    elif("body" in current):
        tag = 'body'
    
    try:
        lang = detect(current[tag])
    except:
        return

    # If not french, we drop the conversation
    if(lang != 'fr'):
        return

    l.append(current)
    if("replies" not in current and "comments" not in current):
        createDialogFromList(root, l)
    else:
        childrenTag = ""
        if("replies" in current): # For comments
            childrenTag = "replies"
        else:   # For posts
            childrenTag = "comments"
        for child in current[childrenTag]:
            DFS(root, current[childrenTag][child], l[:])

def formatData(inputfile, outputfile):
    root = createXML()
    with open(inputfile) as json_data:
        discussions = json.load(json_data)
        for post in discussions:
            DFS(root, discussions[post], [])
    saveXML(root, outputfile);

    print nbOfDialogs

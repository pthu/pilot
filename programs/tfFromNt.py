import glob
import os
import xml.etree.ElementTree as ET
import collections
from unicodedata import category, normalize
from tf.fabric import Fabric
from tf.timestamp import Timestamp


REPO = '~/github/pthu/pilot'
SRC_DIR = os.path.expanduser(f'{REPO}/sources/nt')
TF_DIR = f'{REPO}/tf'

TEI = 'http://www.tei-c.org/ns/1.0'


word1 = 'Αὐτούς·Αὐτούς '
word2 = 'Σιλωάμ?̔ὃ'

for word in (word1, word2):
    print([category(x) for x in word])
    print([x for x in normalize('NFD', word)])
    print([category(x) for x in normalize('NFD', word)])


letter = {'L'}
dia = {'M'}
NFD = 'NFD'


def splitPuncSimple(w):
    afterWord = len(w)
    for i in range(len(w) - 1, -1, -1):
        if category(w[i])[0] not in letter:
            afterWord = i
        else:
            break
    return (w[0:afterWord], w[afterWord:] + ' ')


def splitPunc(w):
    pP = 0
    for i in range(len(w)):
        if category(w[i])[0] not in letter:
            pP += 1
        else:
            break
    preWord = w[0:pP] if pP else ''
    pW = pP
    for i in range(pP, len(w)):
        if category(w[i])[0] in letter:
            pW += 1
        else:
            break
    word = w[pP:pW]
    pA = pW
    for i in range(pW, len(w)):
        if category(w[i])[0] not in letter:
            pA += 1
        else:
            break
    afterWord = w[pW:pA]
    if pA == len(w):
        afterWord += ' '

    rest = splitPunc(w[pA:]) if pA < len(w) else ()
    return ((preWord, word, afterWord),) + rest


def plainCaps(w):
    return ''.join(x.upper() for x in normalize(NFD, w) if category(x)[0] not in dia)


for word in (word1, word2):
    print(splitPunc(word))


tm = Timestamp()
TF = Fabric(locations=TF_DIR)


class Data:
    def __init__(self, bookEn):
        self.bookEn = bookEn
        self.tfFromXml = {}
        self.xmlFromTf = {}
        self.nodeNum = 1
        self.maxSlot = 0
        self.maxNode = 0
        self.paths = {}
        self.nodeFeatures = collections.defaultdict(dict)
        self.edgeFeatures = collections.defaultdict(dict)


book = None
chapter = None
verse = None


def walkNode(node):
    global book
    global chapter
    global verse

    n = data.nodeNum
    if node.tag == f'{{{TEI}}}div':
        xType = node.attrib['type']
        if xType == 'edition':
            book = n
            data.nodeFeatures['otype'][n] = 'book'
            data.nodeFeatures['book'][n] = data.bookEn
            data.nodeNum += 1
        else:
            xSubType = node.attrib['subtype']
            if xSubType == 'chapter':
                chapter = n
                data.nodeFeatures['otype'][n] = 'chapter'
                data.nodeFeatures['chapter'][n] = int(node.attrib['n'])
                data.nodeNum += 1
            elif xSubType == 'verse':
                verse = n
                data.nodeFeatures['otype'][n] = 'verse'
                data.nodeFeatures['verse'][n] = int(node.attrib['n'])
                data.nodeNum += 1
                if len(node) == 0:
                    n = data.nodeNum
                    data.nodeFeatures['otype'][n] = 'word'
                    data.nodeFeatures['orig'][n] = ''
                    data.nodeFeatures['main'][n] = ''
                    data.nodeFeatures['plain'][n] = ''
                    for parent in (book, chapter, verse):
                        data.edgeFeatures['oslots'].setdefault(parent, []).append(n)
                    data.nodeNum += 1
    if node.tag == f'{{{TEI}}}p':
        for elem in node.iter():
            if elem.tag == f'{{{TEI}}}milestone':
                unit = elem.attrib['unit']
                unitAssigned = False
            else:
                unit = None
            if elem.tag == f'{{{TEI}}}pb':
                page = elem.attrib['n']
                pageAssigned = False
            else:
                page = None
            for wordStr in (elem.text, elem.tail):
                if wordStr:
                    for word in wordStr.split():
                        for (preWord, midWord, postWord) in splitPunc(word):
                            n = data.nodeNum
                            if unit and not unitAssigned:
                                data.nodeFeatures[unit][n] = '+'
                                unitAssigned = True
                            if page and not pageAssigned:
                                data.nodeFeatures['page'][n] = page
                                pageAssigned = True
                            data.nodeFeatures['otype'][n] = 'word'
                            data.nodeFeatures['orig'][n] = f'{preWord}{midWord}{postWord}'
                            data.nodeFeatures['main'][n] = midWord
                            data.nodeFeatures['plain'][n] = plainCaps(midWord)
                            if preWord != '':
                                data.nodeFeatures['pre'][n] = preWord
                            if postWord != '':
                                data.nodeFeatures['post'][n] = postWord
                            for parent in (book, chapter, verse):
                                data.edgeFeatures['oslots'].setdefault(parent, []).append(n)
                            data.nodeNum += 1
    for child in node:
        walkNode(child)


def getNode(root):
    global data

    found = False
    for tsElem in root.iter(f'{{{TEI}}}titleStmt'):
        if found:
            break
        for tElem in tsElem.findall(f'{{{TEI}}}title'):
            title = tElem.text
            comps = title.split(' - ', maxsplit=1)
            if len(comps) == 2 and comps[0].lower() == 'new testament':
                bookEn = comps[1].strip()
                found = True
                break
    if not found:
        tm.error('No book name found')
        return
    tm.info(f'Book = {bookEn}')
    data = Data(bookEn)

    for txElem in root.iter(f'{{{TEI}}}body'):
        walkNode(txElem)
    data.maxNode = data.nodeNum - 1


def checkSections():
    noSlots = []
    for n in range(1, data.maxNode + 1):
        nType = data.nodeFeatures['otype'][n]
        if nType != 'word':
            if n not in data.edgeFeatures['oslots']:
                noSlots.append(n)
    print(f'{len(noSlots)} nodes without slots')
    for n in noSlots[0:10]:
        nType = data.nodeFeatures['otype'][n]
        print(f'{nType} {n} has no slots')


def reorder():
    otypeValues = set(data.nodeFeatures['otype'].values())
    otypeRank = dict(((val, ' ' if val == 'word' else val) for val in otypeValues))
    newIds = sorted(
        range(1, data.maxNode + 1),
        key=lambda n: (otypeRank[data.nodeFeatures['otype'][n]], n),
    )
    mapping = dict(((v, i + 1) for (i, v) in enumerate(newIds)))

    orderedFeatures = {}
    for (name, dat) in data.nodeFeatures.items():
        orderedFeatures[name] = dict(((mapping[n], v) for (n, v) in dat.items()))
    data.nodeFeatures = orderedFeatures

    orderedFeatures = {}
    for (name, dat) in data.edgeFeatures.items():
        orderedFeatures[name] = {mapping[n]: [mapping[m] for m in v] for (n, v) in dat.items()}
    data.edgeFeatures = orderedFeatures


data = None

tm.indent(reset=True)
tm.info('Scanning XML sources of NT books found')
for xmlfile in glob.glob(SRC_DIR + '/*.xml'):
    tm.indent(level=1, reset=True)
    (dirName, baseName) = os.path.split(xmlfile)
    (fileName, extension) = os.path.splitext(baseName)
    tm.info(f'parsing {fileName}')
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    getNode(root)
tm.indent(level=0)
tm.info('Processing data ...')
reorder()
checkSections()
data.nodeFeatures['book@en'] = data.nodeFeatures['book']
tm.info(f'Done: collected {data.maxNode} nodes')


numberFeatures = {'chapter', 'verse'}

metaData = {
    '': dict(
        createdBy='Ernst Boogert and Dirk Roorda',
    ),
    'otext': {
        'sectionFeatures': 'book,chapter,verse',
        'sectionTypes': 'book,chapter,verse',
        'fmt:text-orig-full': '{orig} ',
        'fmt:text-orig-main': '{main} ',
        'fmt:text-orig-plain': '{plain} ',
    },
    'book@en': {
        'valueType': 'str',
        'language': 'English',
        'languageCode': 'en',
        'languageEnglish': 'english',
    },
}


sorted(data.nodeFeatures.keys())


for nf in data.nodeFeatures:
    metaData.setdefault(nf, {})['valueType'] = 'int' if nf in numberFeatures else 'str'
for ef in data.edgeFeatures:
    metaData.setdefault(ef, {})['valueType'] = 'int' if ef in numberFeatures else 'str'

TF.save(nodeFeatures=data.nodeFeatures, edgeFeatures=data.edgeFeatures, metaData=metaData)

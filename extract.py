from lxml import etree
import pprint
import operator

def main():
    """ Extract spelling table

        This script extracts the spelling table found
        at: http://en.wikipedia.org/wiki/Spelling_alphabet
        It does not fetch the page nor take the whole page
        as input just the table. It is meant to be single
        use.
    """
    tree = etree.parse(open('table.html'))
    tbody = tree.find('tbody')
    r = {}
    for i, tr in enumerate(tbody.iterchildren()):
        if i == 0:    # first line with titles
            for j, a in enumerate(tr.iterfind('*/a')):
                if a is not None:
                    name = a.get('title')
                    if name is None:
                        name = a.text
                    r[j] = {'label': name}
                    print "setting key to ", name, j
        else:
            key = tr.find('th').text
            if key is None:
                a = tr.find('th').find('a')
                if a is not None:
                    key = a.text
            for j, cell in enumerate(tr.iterfind('td')):
                t = cell.text.strip()
                if t == '-':
                    t = ''
                r[j][key] = t

    print "Extracted the following spelling tables:"
    for alphabet in r.itervalues():
        label = alphabet.pop('label')
        ai = alphabet.items()
        ai.sort(key=operator.itemgetter(0))
        print "Table: ", label
        for item in ai:
            print '%s - %s' % item

    f = open('dict.py', 'wb')
    f.write(pprint.pformat(r))
    f.close()




if __name__ == '__main__':
    main()

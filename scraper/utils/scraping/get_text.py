import re


def get_text(soup):
    INVISIBLE_ELEMS = ('style', 'script', 'head', 'title')
    RE_SPACES = re.compile(r'\s{3,}')

    def visible_texts():
        """ get visible text from a document """
        text = ' '.join([
            s for s in soup.strings
            if s.parent.name not in INVISIBLE_ELEMS
        ])
        # collapse multiple spaces to two spaces.
        return RE_SPACES.sub('  ', text)

    visible_text = visible_texts()
    words = visible_text.lower()

    return [*words.split()]

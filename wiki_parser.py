from py_mini_racer import py_mini_racer

parser_js_filepath = "wtf_wikipedia.js"


class WikiTextParser():

    def __init__(self):
        with open(parser_js_filepath, 'r') as f:
            parser_js_text = f.read()
        self.ctx = py_mini_racer.MiniRacer()
        self.ctx.eval(parser_js_text)

    def parse_wikitext(self, wikitext):
        return self.ctx.call("wtf.parse", wikitext)

    def get_infobox_from_wikitext(self, wikitext):
        try:
            parsed_content = self.parse_wikitext(wikitext)
        except py_mini_racer.JSParseException as e:
            print("Exception parsing wikitext:", flush=True)
            print(wikitext, flush=True)
            print(e, flush=True)
            return {}

        infobox = {}

        if 'infoboxes' in parsed_content and \
                len(parsed_content['infoboxes']) > 0:
            infobox = parsed_content['infoboxes'][0]
        if 'sections' in parsed_content and \
                len(parsed_content['sections']) > 0:
            if 'lists' in parsed_content['sections'][0]:
                infobox['lists'] = parsed_content['sections'][0]['lists']

        return infobox

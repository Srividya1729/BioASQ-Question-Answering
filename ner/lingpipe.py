import os
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict as dd

class Tagger:

	def __init__(self, tag_dict):
		self.dictionary = tag_dict
		self.types = tag_dict.keys()
		self.tags = []

		for key in tag_dict:
			self.tags += tag_dict[key]

	def pretty_print(self):

		print_string = 'TAGS:\n'
		for key in self.dictionary:
			print_string += '\n' + key + '\n'

			for element in self.dictionary[key]:
				print_string += ' ->' + element + '\n'

		print print_string

def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        _dd = dd(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                _dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in _dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def _tag(tag):
	return {
		'entity': tag.get('#text', ''),
		'type': tag.get('@TYPE', '')
	}

def process_xml_lingpipe(xml_string):

	_root = ET.fromstring(xml_string)
	_dict = etree_to_dict(_root)
	relevant_data = _dict['output']['s']
	saved_tags = []

	if isinstance(relevant_data, dict):
		relevant_data = [relevant_data]

	for element in relevant_data:
		for key in element:
			if key == 'ENAMEX':
				tag = element[key]
				if type(tag) == type(list()):
					for t in tag:
						saved_tags.append(_tag(t))
				else:
					saved_tags.append(_tag(tag))

	return saved_tags

def submit_command(input_string, ref='./cmd_ne_en_news_muc6.sh'):

	# call_path = os.getcwd() + '/ling/demos/generic/bin/'
	call_path = 'ner/ling/demos/generic/bin/'
	command_ref = ref
	command_string = 'echo ' + '"%s"' % input_string + ' | ' + command_ref
	output_string = subprocess.check_output(command_string, shell=True, cwd=call_path)

	return output_string


def NER_tagger(doc_id, input_string, method='lingpipe', params=None):

	if method == 'lingpipe':
		input_string = input_string.strip(' ').strip('.') + '. '
		output = submit_command(input_string)
		return process_xml_lingpipe(output)

	return []

def NER_tagger_multiple(doc_ids, input_strings, method='lingpipe', params=None):

	input_string = '. '.join([i.strip(' ').strip('.') for i in input_strings + ['']])

	if method == 'lingpipe':
		if '. ' not in input_string:
			input_string += '. '
		output = submit_command(input_string)
		return process_xml_lingpipe(output)

	return []


# print NER_tagger('Cancer see the Spot. See irrelevant Spot run interesting.')
# tags.pretty_print()

from __future__ import absolute_import, division, print_function

import codecs
import logging
import os

import attr
import six

from bs4 import BeautifulSoup
from zope.interface import implementer

from .utils import APPLE_REF_TEMPLATE, ParserEntry, has_file_with, IParser


log = logging.getLogger(__name__)


PYDOCTOR_HEADER = b'''\
        This documentation was automatically generated by
        <a href="https://github.com/twisted/pydoctor/">pydoctor</a>'''

PYDOCTOR_HEADER_OLD = b'''\
      This documentation was automatically generated by
      <a href="https://launchpad.net/pydoctor/">pydoctor</a>'''

PYDOCTOR_HEADER_REALLY_OLD = b'''\
      This documentation was automatically generated by
      <a href="http://codespeak.net/~mwh/pydoctor/">pydoctor</a>'''


@implementer(IParser)
@attr.s
class PyDoctorParser(object):
    """
    Parser for pydoctor-based documentation: mainly Twisted.
    """
    doc_path = attr.ib()

    name = "pydoctor"

    @classmethod
    def detect(cls, path):
        return has_file_with(
            path, "index.html", PYDOCTOR_HEADER
        ) or has_file_with(
            path, "index.html", PYDOCTOR_HEADER_OLD
        ) or has_file_with(
            path, "index.html", PYDOCTOR_HEADER_REALLY_OLD
        )

    def parse(self):
        """
        Parse pydoctor docs at *doc_path*.

        yield `ParserEntry`s
        """
        soup = BeautifulSoup(
            codecs.open(
                os.path.join(self.doc_path, 'nameIndex.html'),
                mode="r", encoding="utf-8",
            ),
            'lxml'
        )
        for tag in soup.body.find_all(u'a'):
            path = tag.get(u'href')
            data_type = tag.get(u'data-type')
            if path and data_type and not path.startswith(u'#'):
                name = tag.string
                yield ParserEntry(
                    name=name,
                    type=data_type.replace(u"Instance ", u""),
                    path=six.text_type(path)
                )

    def find_and_patch_entry(self, soup, entry):
        link = soup.find(u'a', attrs={'name': entry.anchor})
        if link:
            tag = soup.new_tag(u'a')
            tag['name'] = APPLE_REF_TEMPLATE.format(entry.type, entry.name)
            link.insert_before(tag)
            return True
        else:
            return False
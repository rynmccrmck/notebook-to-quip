#! /usr/bin/python
import click
import nbformat
import os
import quip

from bs4 import BeautifulSoup
from nbconvert import HTMLExporter


QUIP_ACCESS_TOKEN = os.environ.get('QUIP_ACCESS_TOKEN')
quip_client = quip.QuipClient(access_token=QUIP_ACCESS_TOKEN)


def _html_from_notebook(notebook_path):

    with open(notebook_path, 'r') as f:
        notebook_to_convert = f.read()

    notebook = nbformat.reads(notebook_to_convert, as_version=4)

    html_exporter = HTMLExporter()
    html_exporter.template_file = 'basic'

    (body, resources) = html_exporter.from_notebook_node(notebook)
    return body


@click.group()
def cli1():
    pass


@cli1.command()
@click.option('--notebook', default=None, help='Location of the notebook', required=True)
@click.option('--title', required=True, help='The title of the imported document.')
@click.option('--member_ids', default=[], help='''A comma-separated list of folder or user IDs.''')
def new_document(notebook, title, member_ids):
    """Create a new quip from notebook"""
    nb_html = _html_from_notebook(notebook)
    new_doc = quip_client.new_document('', format='html', title=title, 
                                       member_ids=member_ids)
    document_id = new_doc['thread']['id']
    _ = quip_client.edit_document(document_id, content=nb_html)
    print('New docuemnt {} created'.format(document_id))


@cli1.command()
@click.option('--notebook', default=None, help='Location of the notebook', required=True)
@click.option('--document_id', default=None, help='Document ID', required=True)
def replace_document(notebook, document_id):
    """Create a new quip from notebook"""

    nb_html = _html_from_notebook(notebook)

    quip_html = quip_client.get_thread(document_id)['html']
    soup = BeautifulSoup(quip_html)
    section_ids = filter(lambda x: x is not None,
                         [i.get('id') for i in soup.findAll()])
    for section_id in section_ids:
        print('Deleting section {}'.format(section_id))
        quip_client.edit_document(document_id, content='',
                                  operation=quip_client.DELETE_SECTION,
                                  format='html', section_id=section_id)

    _ = quip_client.edit_document(document_id, content=nb_html)
    print('File overwritten {}'.format(document_id))


main = click.CommandCollection(sources=[cli1])
if __name__ == '__main__':
    main()



## EpicSplitter

4 chunks

#### Split 1
154 tokens, line: 11 - 29

```python
from os import path
from typing import Any, Dict, List, Set, Tuple, Union

from docutils.frontend import OptionParser
from docutils.io import FileOutput

from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.config import Config
from sphinx.errors import NoUri
from sphinx.locale import __
from sphinx.util import logging, progress_message
from sphinx.util.console import darkgreen  # type: ignore
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.osutil import ensuredir, make_filename_from_project
from sphinx.writers.manpage import ManualPageTranslator, ManualPageWriter

logger = logging.getLogger(__name__)
```



#### Split 2
173 tokens, line: 32 - 54

```python
class ManualPageBuilder(Builder):
    """
    Builds groff output in manual page format.
    """
    name = 'man'
    format = 'man'
    epilog = __('The manual pages are in %(outdir)s.')

    default_translator_class = ManualPageTranslator
    supported_image_types: List[str] = []

    def init(self) -> None:
        if not self.config.man_pages:
            logger.warning(__('no "man_pages" config value found; no manual pages '
                              'will be written'))

    def get_outdated_docs(self) -> Union[str, List[str]]:
        return 'all manpages'  # for now

    def get_target_uri(self, docname: str, typ: str = None) -> str:
        if typ == 'token':
            return ''
        raise NoUri(docname, typ)
```



#### Split 3
417 tokens, line: 56 - 106

```python
class ManualPageBuilder(Builder):

    @progress_message(__('writing'))
    def write(self, *ignored: Any) -> None:
        docwriter = ManualPageWriter(self)
        docsettings: Any = OptionParser(
            defaults=self.env.settings,
            components=(docwriter,),
            read_config_files=True).get_default_values()

        for info in self.config.man_pages:
            docname, name, description, authors, section = info
            if docname not in self.env.all_docs:
                logger.warning(__('"man_pages" config value references unknown '
                                  'document %s'), docname)
                continue
            if isinstance(authors, str):
                if authors:
                    authors = [authors]
                else:
                    authors = []

            docsettings.title = name
            docsettings.subtitle = description
            docsettings.authors = authors
            docsettings.section = section

            if self.config.man_make_section_directory:
                ensuredir(path.join(self.outdir, str(section)))
                targetname = '%s/%s.%s' % (section, name, section)
            else:
                targetname = '%s.%s' % (name, section)

            logger.info(darkgreen(targetname) + ' { ', nonl=True)
            destination = FileOutput(
                destination_path=path.join(self.outdir, targetname),
                encoding='utf-8')

            tree = self.env.get_doctree(docname)
            docnames: Set[str] = set()
            largetree = inline_all_toctrees(self, docnames, docname, tree,
                                            darkgreen, [docname])
            largetree.settings = docsettings
            logger.info('} ', nonl=True)
            self.env.resolve_references(largetree, docname, self)
            # remove pending_xref nodes
            for pendingnode in largetree.traverse(addnodes.pending_xref):
                pendingnode.replace_self(pendingnode.children)

            docwriter.write(largetree, destination)

    def finish(self) -> None:
        pass
```



#### Split 4
166 tokens, line: 109 - 128

```python
def default_man_pages(config: Config) -> List[Tuple[str, str, str, List[str], int]]:
    """ Better default man_pages settings. """
    filename = make_filename_from_project(config.project)
    return [(config.root_doc, filename, '%s %s' % (config.project, config.release),
             [config.author], 1)]


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_builder(ManualPageBuilder)

    app.add_config_value('man_pages', default_man_pages, None)
    app.add_config_value('man_show_urls', False, None)
    app.add_config_value('man_make_section_directory', False, None)

    return {
        'version': 'builtin',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
```

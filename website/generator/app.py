#!/usr/bin/env python

from functools import partial
from flask import Flask, abort, request, Markup, render_template
import jinja2
import yaml
import os


import misaka as markdown
import houdini
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name

app = Flask(__name__)

# this is taken straightly from the misaka docs
# but the lexer check is new, better this way around upstream?
class HighlighterRenderer(markdown.HtmlRenderer):
    def blockcode(self, text, lang):
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = None

        if lexer:
            # Fixme: it would be better to have a single css file created,
            # which is possible! but right now in this early phase that's
            # a distraction
            formatter = HtmlFormatter(noclasses=True)
            return highlight(text, lexer, formatter)
        # no lexer
        return '\n<pre><code>{}</code></pre>\n'.format(
                houdini.escape_html(text.strip()))


renderer = HighlighterRenderer()
md = markdown.Markdown(renderer, extensions=('fenced-code', 'autolink'
                        , 'quote', 'footnotes', 'strikethrough', 'tables'))

def extractPageData(data):
    lines = data.splitlines(True)
    if lines[0].strip() != '```yaml':
        return data, {}

    lines = lines[1:]
    yamlData=None
    for i, line in enumerate(lines):
        if line.strip() == '```':
            yamlData = ''.join(lines[:i])
            lines = lines[i+1:]
            break
    if yamlData is None:
        return data, {}

    try:
        parsed = yaml.load(yamlData)
    except yaml.YAMLError as exc:
        return data, {}

    return ''.join(lines), parsed


def genericFileRenderer(rootpath, sourcedir, config, filename):
    # FIXME: this should obey the maxdepth configuration!
    # also, should be normalized and not start with ..
    noramlfilename = os.path.normpath(filename)
    if noramlfilename.startswith('.'):
        # above root
        abort(404)
    if len(noramlfilename.split('/')) > config.get('maxdepth', float('inf')):
        abort(404)

    # nice, filename is indeed something like path/to/file.md
    # in http://localhost:5000/web/Proposals/path/to/file.md
    # so, the <path: converter works well!
    if not noramlfilename.endswith('.md'):
        return 'Hello World: ' + sourcedir + ' => ' + noramlfilename;

    path = [rootpath]
    if sourcedir:
        path.append(sourcedir)
    path.append(noramlfilename)
    print(path, path)
    try:
        with open(os.path.join(*path)) as f:
            data = f.read()
    except FileNotFoundError:
        abort(404)

    content, pageData = extractPageData(data)

    print('pageData:', pageData)

    return render_template(
          config.get('template', 'standard.html')
        , title=filename
        , content=Markup(md(content))
    )

def buildRoutes(rootpath, app, config, parent=None):
    for key, setup in config.items():
        target = '/'.join([parent, key]) if parent else key
        # if source is not defined, target is considered the name of the source dir
        # should this inherit from parent?
        # TODO: This nested definition is a bit twisted and maybe stupid.
        #       I should reevaluate how this works.
        #       In the example doc above, if maxdepth: 1 is not set, there
        #       are 2 ways to interpret Proposals. Should probably be
        #       easier not to be ambigous. Though, I think the web/Proposals
        #       endpoint would win.
        source = setup.get('source', key)
        suffix = setup.get('suffix', '')
        rule = '/{target}/<path:filename>{suffix}'.format(target=target, suffix=suffix)
        # do we need to remove the slashes? for url_for maybe?
        endpoint = target#.replace('/', '.')
        print('rule:', rule, 'source:', source, endpoint)
        # Todo: make 'genericFileRenderer' configurable
        # actually, since we pass setup here, the branching could
        # happen in there. rename to sth?
        # also, could be an instance with a __call__ method
        viewFunc = partial(genericFileRenderer, rootpath, source, setup)
        app.add_url_rule(rule, endpoint, viewFunc)
        if 'children' in setup:
            # recurse
            buildRoutes(rootpath, app, setup['children'], target)

"""
let's say for the target web/Proposals I want to walk down
the Proposals dir.
"""

# the keys are the root target dirs

configYAML = u"""
template_folder: website/templates
sources:
    web:
        # more configuration for the target can go here, some of which
        # could be overwritten by the inputs config
        source: '' # overwrite the source dir to be the directory root
        maxdepth: 1 # defaults to float('inf') and 0 turns the input channel off
        # template:
        # template_vars?
        suffix: '.html' # maybe rather as a types config?, though that could default to this
        types:
            md: {} # type specific config, template vars etc...
        children:
            # These keys are paths from the repository root to directories.
            # They may contain slashes
            Proposals:
                suffix: '.html'
                template: proposals.html
                types:
                    # this are file name suffixes and configuration how to treat
                    # then
                    md: {} # type specific config, template vars etc...
"""

config = yaml.load(configYAML)
rootpath = '.' # cwd currently, path/to/repository then

print(config);

if 'template_folder' in config:
    # load templates first from the directory defined by the repository, then
    # by the default loader i.e. from the app.
    jinja2_loader = jinja2.ChoiceLoader([
            # first local
            jinja2.FileSystemLoader(os.path.join(rootpath, config['template_folder'])),
            # then the default
            app.jinja_loader
    ])
    app.jinja_loader = jinja2_loader

if 'sources' in config:
    buildRoutes(rootpath, app, config['sources'])

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)

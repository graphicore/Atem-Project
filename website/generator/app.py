#!/usr/bin/env python

from functools import partial
from flask import Flask, abort, request, Markup, render_template
from flask_frozen import Freezer
import jinja2
import yaml
import os, sys


import misaka as markdown
import houdini
from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name


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
    default =  data, {}
    lines = data.splitlines(True)
    if lines[0].strip() != '```yaml':
        return default

    lines = lines[1:]
    yamlData=None
    for i, line in enumerate(lines):
        if line.strip() == '```':
            yamlData = ''.join(lines[:i])
            lines = lines[i+1:]
            break
    if yamlData is None:
        return default

    try:
        parsed = yaml.load(yamlData)
    except yaml.YAMLError as exc:
        return default

    return ''.join(lines), parsed


def makePath(*pathparts):
    path = []
    for part in pathparts:
        if part:
            path.append(part)
    return os.path.join(*path)

def readSourceFile(path):
    try:
        with open(path) as f:
            data = f.read()
    except FileNotFoundError:
        return False, None, None

    content, pageData = extractPageData(data)
    return True, content, pageData

def getTypeSetup(config, filename):
    """
        get the type setup via the filename suffix
    """
    _, suffix = os.path.splitext(filename)
    # remove the dot, if any
    # This way, we can define an '' empty key target entry to handle
    # files without type/extension
    suffix = suffix[1:]
    if not 'types' in config or not suffix in config['types']:
        return False, None, None
    # may also be defined as `null` or otherwise falsy which becomes
    # an empty dict.
    setup = config['types'].get(suffix) or {}
    return True, suffix, setup

def prepareContent(typeSetup, typeKey, content):
    contentType = typeSetup.get('type', typeKey)
    if contentType == 'md':
        content = Markup(md(content))
    elif contentType == 'htmlpart':
        content = Markup(content)
    elif contentType == 'txt':
        # content = content
        # because we don't make it a Markup instance this will be
        # html-escaped by jinja2
        pass
    else:
        # no defaulting, this is a programming error
        raise Exception('Unkown contentType, don\'t know how to treat "{0}".'
                                                        .format(contentType))
    return content


def checkFileForEndpoint(config, filename, pathparts):
    original = filename
    # this way we can request 'index' and respond with 'index.md'

    if 'file_map' in config:
        if filename in config['file_map']:
            filename = config['file_map'][filename]
        elif filename in config['file_map'].values():
            # rather redirect?
            # this is to prevent files being created twice for the same
            # source, i.e.  /index.html and /index.md.html
            return False, 404

    success, typeKey, typeSetup = getTypeSetup(config, filename)
    if not success:
        # no setup for the type
        return False, 404

    normalfilename = os.path.normpath(filename)
    if normalfilename.startswith('.'):
        # above root
        return False, 404

    if normalfilename.count(os.path.sep) >= config.get('maxdepth', float('inf')):
        return False, 404


    filePath = makePath(* pathparts + [normalfilename])
    if not os.path.isfile(filePath):
        return False, 404

    return True, (filePath, typeKey, typeSetup)

def genericFileRenderer(rootpath, sourcedir, config, filename):
    # nice, filename is indeed something like path/to/file.md
    # in http://localhost:5000/web/Proposals/path/to/file.md
    # so, the <path: converter works well!
    success, result = checkFileForEndpoint(config, filename, [rootpath, sourcedir])
    if not success:
        abort(result or 404)
    filePath, typeKey, typeSetup = result

    # the file actually does not exist!
    success, content, pageSetup = readSourceFile(filePath)
    if not success:
        abort(404)

    viewVars = {
        'title': filename
      , 'content': prepareContent(typeSetup, typeKey, content)
    }

    # The most specific setup overrides the less specific
    # i.e. pageData can set the "template"
    # also, content can be overridden, which may be useful in some fringe cases
    # but usually I think this is not used
    # This put's a lot of power to the content files, which is intended.
    # I don't want to update the generator too often for trivial things.
    # Also, keep in mind that I expect the content authors to be aware
    # of their responsibility and not to have malicious intentions (project
    # commit rights imply this kind of trust).
    for item in [config, typeSetup, pageSetup]:
        viewVars.update(item)

    template = viewVars.get('template', 'standard.html')
    return render_template(template, **viewVars)

def buildRoutes(rootpath, app, config, parent=None):
    targets = []
    defaults = config.get('source_defaults', {});
    # if no "targets" are defined, this will not define any endpoints
    for target, setup in config.get('targets', {}).items():
        # if source is not defined, target is considered the name of the source dir
        targetSetup = {}
        for item in [defaults, setup]:
            targetSetup.update(item)
        # This can't be overridden by source_defaults, would be kind of
        # against the point.
        source = setup.get('source', target)
        # .html is in the most cases a sensible choice, because of our target,
        # to produce static html files a webserver could determine this way
        # a mime type of text/html. This is actually a recommendation by
        # frozen flask, which is going to be used.
        suffix = targetSetup.get('suffix', '')
        if target:
            targetToken = '{0}/'.format(target)
            # do we need to remove the slashes? for url_for maybe?
            endpoint = target #.replace('/', '.')
        else:
            # this is the website root target
            targetToken = ''
            endpoint = '__root__'
        indexEndpoint = endpoint + '.index'
        rule = '/{target}<path:filename>{suffix}'.format(target=targetToken, suffix=suffix)
        indexRule = '/{target}'.format(target=targetToken)

        # TODO: remove when everything is set up
        print('rule:', rule, 'source:', source, endpoint)

        viewFunc = partial( genericFileRenderer
                          , rootpath
                          , source
                          , targetSetup
        )
        app.add_url_rule(rule, endpoint, viewFunc)

        # special case for index.html for this target
        # This is a problem, because it has no variable part in the url
        # frozen flask tries to request it always. Regardless if the
        # url generator yields it or not. The subsequent 404 answer
        # is handled badly by frozen flask.
        viewFunc = partial( genericFileRenderer
                          , rootpath
                          , source
                          , targetSetup
                          , filename='index'
        )
        app.add_url_rule(indexRule, indexEndpoint, viewFunc)

        targets.append({
            'source': source
          , 'config': targetSetup
          , 'endpoint': endpoint
          , 'indexEndpoint': indexEndpoint
          , 'suffix': suffix
          , 'rootpath': rootpath
        })

    return targets;


def makeApp(rootpath, configFileName='webgenerator.yaml'):
    app = Flask(__name__)

    # If configFileName is unusable for any reason we want this to fail
    # the point of this method is to bootstrap app from configFile
    with open(os.path.join(rootpath, configFileName), 'r') as configFile:
        config = yaml.load(configFile)

    # Todo, this should be possible as a list, so we could include
    # external templates as well
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
    targets = buildRoutes(rootpath, app, config)
    return app, targets


# Todo: make url generators for the defined targets using the configuration
def getEndpoints(target, filename, checkFileMap=True):
    config = target['config']
    rootpath = target['rootpath']
    source = target['source']
    success, _ = checkFileForEndpoint(config, filename, [rootpath, source])
    if not success:
        # this would make a 404
        return

    files = []
    if checkFileMap and 'file_map' in config and filename in config['file_map'].values():
        # file_map will be used to generate these requests
        return

    # Only a index.html can create this shorter url
    if filename + target['suffix'] == 'index.html':
        yield target['indexEndpoint'], {}
    else:
        yield target['endpoint'], {'filename': filename}

def genericURLGenerator(targets):  # Some other function name
    """
        This yields `(endpoint, values)` tuples

        You can specify a different endpoint by yielding a (endpoint, values)
        tuple instead of just values, or you can by-pass
        url_for and simply yield URLs as strings.

        targets is a list of dictionaries
        {
            'source': source
          , 'config': targetSetup
          , 'endpoint': endpoint
          , 'indexEndpoint': indexEndpoint
          , 'suffix': suffix
          , 'rootpath': rootpath
        }
    """
    for target in targets:
        maxDepth = target['config'].get('maxdepth', float('inf'))
        if maxDepth == 0:
            continue
        # http://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
        for root, dirs, files in os.walk('.' if target['source'] == '' else target['source']):
            depth = root.count(os.path.sep) + 1
            if depth >= maxDepth:
                # This is a the magic piece, it modifies the list that is
                # used by the os.walk iterator.
                # Deeper dirs won't be visited...
                del dirs[:]
            if depth > maxDepth:
                continue
            for filename in files:
                yield from getEndpoints(target, filename)
            for filename in target['config'].get('file_map', {}):
                yield from getEndpoints(target, filename, checkFileMap=False)

if __name__ == '__main__':
    # first argument sets rootpath
    rootpath = sys.argv[-1] if len(sys.argv) >= 2 else os.getcwd()
    app, targets = makeApp(rootpath)
    if len(sys.argv) >= 3:
        app.config.update(
            FREEZER_RELATIVE_URLS=True
          , FREEZER_DESTINATION=os.path.abspath(sys.argv[1])
        )
        freezer = Freezer( app
                           # We'll have to request all pages manually. This
                           # way we can create some endpoints pro forma
                           # without yielding 404 errors.
                         , with_no_argument_rules=False)
        freezer.register_generator(partial(genericURLGenerator, targets))
        freezer.freeze()
    else:
        app.run(debug=True)

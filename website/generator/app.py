#!/usr/bin/env python

from functools import partial, wraps
from datetime import datetime
import subprocess
import os, sys, stat, shutil, tempfile
from io import StringIO

from flask import Flask, abort, request, Markup, render_template, url_for \
                , send_from_directory, render_template_string
from flask_frozen import Freezer, relative_url_for
from werkzeug.contrib.atom import AtomFeed
from urllib.parse import urljoin
import jinja2
import yaml



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
    return os.path.abspath(os.path.join(*path))

def readSourceFile(path):
    try:
        with open(path) as f:
            data = f.read()
    except FileNotFoundError:
        return False, None, None

    content, pageData = extractPageData(data)
    return True, content, pageData

def checkTypeSetup(config, filename):
    """
        get the type setup via the filename suffix
    """
    _, suffix = os.path.splitext(filename)
    # remove the dot, if any
    # This way, we can define an '' empty key target entry to handle
    # files without type/extension
    typeKey = suffix[1:]
    types = config.get('types', None)
    fail = False, None

    if types is None:
        return fail

    if typeKey in types:
        pass
    elif '*' in types:
        typeKey = '*'
    else:
        return fail

    # May be defined falsy which always becomes an empty dict.
    typeSetup = types.get(typeKey, None) or {}
    return True, dict(typeKey=typeKey, typeSetup=typeSetup)

def prepareContent(contentType, content, context):

    if not context.get('skip_content_templating', False):
        if 'source' in context:
            context = context.copy()
            del context['source']
        content = render_template_string(content, **context)

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
        raise ValueError('Unkown contentType, don\'t know how to treat "{0}".'
                                                        .format(contentType))
    return content

_defaultMarker = object()

class FileDataCache(object):
    def __init__(self):
        self._files = {}

    def get(self, path, default=_defaultMarker):
        f = self._files.get(path, None)
        if f is None:
            success, content, setup = readSourceFile(path)
            if not success:
                if default is not _defaultMarker:
                    return default
                raise KeyError('Can\'t read file at "{0}".'.format(path))
            f = self._files[path] = FileCacheItem(path, content, setup)
        return f

class FileCacheItem(object):
    def __init__(self, path, content, setup):
        self.path = path
        self.content = content
        self.setup = setup
        self._times = None

    def _getGitDate(self, filename, diffFilter):
        """
            diff-filter=A === added date
            diff-filter=M === modified date
        """
        p = subprocess.Popen(['git', 'log' , '--diff-filter={0}'.format(diffFilter)
                            , '--follow', '--format=%at', '-1', '--', filename]
                            , stdout=subprocess.PIPE
                            # Ask the git repository that contains
                            # the file, if any.
                            , cwd=os.path.dirname(filename)
                            )
        out, err = p.communicate()
        # out = b'1464452704\n' OR b''
        timestamp = out.strip()
        if not timestamp:
            # also if file is not in git at all
            return None
        datetime.fromtimestamp(float(timestamp))

    def _getStatDates(self, filename):
        statData = os.stat(filename)
        return tuple([datetime.fromtimestamp(statData[i])
                            for i in (stat.ST_CTIME, stat.ST_MTIME)])

    def _getTimes(self):
        """
        return a tuple of 2 datetime objects representing creation and
        modification dates.

        Ask git for the creation (added) time and modification time of the File.

        If git can't provide an answer(maybe because the file was never
        added to git, or not modified after adding) use os.stat instead.
        """

        ctime = self._getGitDate(self.path, 'A')
        if not ctime:
            return self._getStatDates(self.path)

        mtime = self._getGitDate(self.path, 'M')
        if not mtime:
            mtime = self._getStatDates(self.path)[1]

        return ctime, mtime

    @property
    def times(self):
        """ A tuple of 2 datetime objects representing creation and
        modification dates.
        """
        if not self._times:
            self._times = self._getTimes()
        return self._times;


def checkFileForEndpoint(target, filename):
    config = target['config']
    pathparts = target['pathparts']
    rendererConfig = renderers[target['rendererName']][1]

    result = {}
    # this way we can request 'index' and respond with 'index.md'

    file_map = config.get('file_map', False)
    file_mapped = False
    if file_map:
        if filename in file_map:
            filename = file_map[filename]
            file_mapped = True
        elif filename in file_map.values():
            # rather redirect?
            # this is to prevent files being created twice for the same
            # source, i.e.  /index.html and /index.md.html
            return False, 404

    result['filename'] = filename

    checkTypeSetup = rendererConfig.get('checkTypeSetup', False)
    if checkTypeSetup:
        success, checkTypeSetupResult = checkTypeSetup(config, filename)
        if not success:
            # no setup for the type
            return False, 404
        result.update(checkTypeSetupResult)

    normalfilename = os.path.normpath(filename)
    if normalfilename.startswith('.'):
        # above root
        return False, 404

    if normalfilename.count(os.path.sep) >= config.get('maxdepth', float('inf')):
        return False, 404

    filePath = makePath(* pathparts + [normalfilename])
    if not os.path.isfile(filePath):
        return False, 404
    result.update(filePath=filePath)

    return True, result

def staticRenderer(app, config, fileData):
    directory, filename = os.path.split(fileData['filePath'])
    try:
        return send_from_directory(directory, filename)
    except Exception as e:
        raise e
    return result


def renderContent(config, typeData, fileItem):
    typeSetup = typeData['typeSetup']
    typeKey = typeData['typeKey']
    contentType = typeSetup.get('type', typeKey)

    context = {}
    for item in [config, typeSetup, fileItem.setup]:
        if item: context.update(item)

    content = prepareContent(contentType, fileItem.content, context)
    return content, context

def templatedRenderer(app, config, fileData):
    fileItem = app.config['fileDataCache'].get(fileData['filePath'], None)

    if not fileItem:
        # the file actually does not exist!
        abort(404)

    content, context = renderContent(config, fileData, fileItem)

    viewVars = {
        'title': fileData['filename']
      , 'content': content
    }
    viewVars.update(context)
    template = viewVars.get('template', 'standard.html')
    return render_template(template, **viewVars)

def fileless_view(config):
    template = config.get('template', 'standard.html')
    return render_template(template, **config)

def file_view(app, rendererConfig, target, filename):
    # nice, filename is indeed something like path/to/file.md
    # in http://localhost:5000/web/Proposals/path/to/file.md
    # so, the <path: converter works well!

    endpointConfig = target['config']

    success, result = checkFileForEndpoint(target, filename)
    if not success:
        abort(result or 404)

    fileData = result

    ###
    # The most specific setup overrides the less specific
    # i.e. pageData can set the "template"
    # also, content can be overridden, which may be useful in some fringe cases
    # but usually I think this is not used
    # This put's a lot of power to the content files, which is intended.
    # I don't want to update the generator too often for trivial things.
    # Also, keep in mind that I expect the content authors to be aware
    # of their responsibility and not to have malicious intentions (project
    # commit rights imply this kind of trust).

    # TODO: delete, I don't think anymore it's a good idea to do this
    # config = {}
    # for item in [app.config, endpointConfig]:
    #     config.update(item)

    fn = rendererConfig.get('renderer')
    return fn(app, endpointConfig, fileData)

def feed_view(app, target):
    menu = app.config['menu']
    config = target['config']
    defaultAuthor = config.get('feed_author', None)
    endpoint = target['endpoint']


    # We need to configure a url_root when freezing!
    # This is best app wide config
    url_root = app.config.get('url_root', request.url_root)
    feed_title = config.get('feed_title', 'Feed for: {0}'.format(endpoint))
    # as id and link rel="self"
    feed_url = urljoin(url_root, request.path)

    feedArgs = {'feed_url': feed_url}

    indexEndpoint = target.get('indexEndpoint', None)
    if indexEndpoint is not None:
        # where to find the html version
        feedArgs['url'] = urljoin(url_root, url_for(indexEndpoint))
    if defaultAuthor is not None:
        feedArgs['author'] = defaultAuthor
    feed = AtomFeed(feed_title, **feedArgs)

    i = 0
    maxitems = config.get('feed_maxitems', 10)
    for url, name, active, meta in menu.get([endpoint], sortorder='ctime',
                                    reverse=True, include_meta=True):
        i += 1
        if i >= maxitems: break

        # use the unpatched url_for to get a complete path
        # menu uses the version provided by frozen flask
        abs_url = url_for(meta['endpoint'], **meta['viewArgs'])
        app_root_path = abs_url[:-len(url)]

        if url[0] == '/':
            url = url[1:]
        xml_base = urljoin(url_root, app_root_path)
        fileItem = meta['fileItem']
        published, updated = fileItem.times

        _, typeData = checkTypeSetup(config, meta['viewArgs']['filename'])
        content, _ = renderContent(config, typeData, fileItem)

        global_url = urljoin(xml_base, url)

        feedData = dict(
              title = fileItem.setup.get('title', name)
            , content = content
            , content_type = 'html'
            , url = global_url
            , published = published
            , updated = updated
            , xml_base = xml_base
            , id = global_url
        )
        summary = title = fileItem.setup.get('summary', None)
        if summary is not None:
            feedData.update(
                summary=summary
                , summary_type='text'
            )

        # TODO: fileItem could get the committers name/email from git possibly
        author = fileItem.setup.get('author', None)

        if author is None and defaultAuthor is None:
            # Required if the feed does not have an author element.
            author = '(unknown author)'
        if author is not None:
            feedData['author'] = author

        feed.add(**feedData)
    return feed.get_response()

def init_feed(app, target, renderer):
    if not target['config'].get('add_feed', False):
        return None, None
    feedRule = '{0}feed.atom'.format(target['ruleBase'])
    feedEndpoint = '{0}.feed'.format(target['endpoint'])
    viewFunc = partial(feed_view, app, target)
    rule = (feedRule, feedEndpoint, viewFunc)
    return rule, dict(feedEndpoint=feedEndpoint)

def init_fileEndpoint(app, target, renderer):
    targetName = target['name']
    config = target['config']
    if targetName:
        ruleBase = '/{0}/'.format(targetName)
        endpoint = targetName
    elif targetName == '':
        # The empty string is the website root target, a special case
        ruleBase = '/'
        endpoint = '__root__'
    else:
        raise ValueError('Don\'t know how to treat falsy target "{0}".'.format(targetName))

    fileRule = '{0}<path:filename>{1}'.format(ruleBase, target.get('suffix',''))
    pathparts = [app.config['rootpath'], target['source']]
    rendererFunction, rendererConfig = renderer
    viewFunc = partial( rendererFunction
                      , app
                      , rendererConfig
                      , target
    )
    rule = (fileRule, endpoint, viewFunc)
    return rule, dict(
                    endpoint=endpoint
                  , ruleBase=ruleBase
                  , pathparts=pathparts
                  )

def init_indexEndpoint(app, target, renderer):
    indexEndpoint = '{0}:index'.format(target['endpoint'])
    indexRule = target['ruleBase']
    rendererFunction, rendererConfig = renderer
    # special case for index.html for this target
    # Because it has no variable part in the url frozen flask tries
    # to request it by default, always unless the with_no_argument_rules
    # argument of Freezer is False, which is in this case.
    viewFunc = partial( rendererFunction
                      , app
                      , rendererConfig
                      , target
                      # regardless of the suffix, this should always be
                      # index.html, otherwise, this is not an index endpoint.
                      # Though, webservers could be configured differently, but
                      # index.html is the default.
                      , filename='index.html'
    )
    rule = (indexRule, indexEndpoint, viewFunc)
    return rule, dict(indexEndpoint=indexEndpoint)

def init_fileSource(app, target, renderer):
    source = target['config'].get('source', target['name'])
    return None, dict(source=source)

def init_fileSuffix(app, target, renderer):
    # important! only for 'templated'
    suffix = target['config'].get('suffix', None)
    targetUpdate = {}
    if suffix: targetUpdate['suffix'] = suffix
    return None, targetUpdate

def init_fileLess(app, target, renderer):
    targetName = target['name']
    ruleName = '/{0}'.format(targetName)
    endpoint = targetName
    config = target['config']
    rendererFunction, rendererConfig = renderer
    viewFunc = partial(rendererFunction, config)
    rule = (ruleName, endpoint, viewFunc)
    return rule, dict(endpoint=endpoint)

renderers = {
    'static': (file_view, {
                  'renderer': staticRenderer
                , 'checkTypeSetup': False
                , 'init': [
                          init_fileSource
                        , init_fileEndpoint
                        , init_indexEndpoint
                        ]


                })
  , 'templated': (file_view, {
                  'renderer': templatedRenderer
                , 'checkTypeSetup': checkTypeSetup
                , 'init': [
                          init_fileSource
                        , init_fileSuffix
                        , init_fileEndpoint
                        , init_indexEndpoint
                        , init_feed
                        ]
                })
  , 'fileless': (fileless_view, {
                  'init': [ init_fileLess ]
                })
}

def buildRoutes(app, config, parent=None):
    targets = []
    defaults = config.get('source_defaults', {});
    # "source" can't be overridden by source_defaults, would be kind of
    # against the point.
    if 'source' in defaults:
        raise ValueError('config["source_defaults"] must not define "source", ' \
                + 'but it is set to "{0}"'.format(defaults['source']))

    # if no "targets" are defined, this will not define any endpoints
    for targetName, setup in config.get('targets', {}).items():
        # if source is not defined, target is considered the name of the source dir
        targetConfig = {}
        for item in [defaults, setup]:
            targetConfig.update(item)

        rendererName = setup.get('renderer', 'templated')
        rendererFunction, rendererConfig = renderer = renderers[rendererName]

        target = {
            'name': targetName
          , 'rendererName': rendererName
          , 'config': targetConfig
        }

        for fun in rendererConfig['init']:
            # The order of the functions in init is important, because
            # they update "target" and latter functions are dependent
            # on the values set by former functions
            rule, targetUpdate = fun(app, target, renderer)
            if rule: app.add_url_rule(*rule)
            if targetUpdate: target.update(targetUpdate)

        targets.append(target)

    return targets;

def makeApp(rootpath, configFileName='webgenerator.yaml'):
    # If configFileName is unusable for any reason we want this to fail
    # the point of this method is to bootstrap app from configFile
    with open(os.path.join(rootpath, configFileName), 'r') as configFile:
        config = yaml.load(configFile)

    app = Flask(__name__)

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

    app.config['rootpath'] = rootpath
    targets = buildRoutes(app, config)
    app.config['fileDataCache'] = FileDataCache()
    menu = Menu(app, targets)
    app.config['menu'] = menu
    app.config['generator_config'] = config
    return app, menu

def fileURLGenerator(target, filename, fromFileMap=False):
    config = target['config']
    success, result = checkFileForEndpoint(target, filename)
    if not success:
        # this would make a 404
        return

    if not fromFileMap:
        file_map = config.get('file_map', None)
        if file_map and filename in file_map.values():
            # file_map will be used to generate these requests
            return

    # if the name comes from the file_map we don't add a suffix
    # and yield the filename directly
    # This is only interesting for the "index.html" mapping at the moment
    # anyways! All the other files would have to obey the rules of the
    # target
    suffix = '' if fromFileMap else target.get('suffix', '')

    indexEndpoint = target.get('indexEndpoint', None)
    # Only a index.html can create this shorter url
    if indexEndpoint is not None and '{0}{1}'.format(filename, suffix) == 'index.html':
        yield indexEndpoint, {}, result['filePath']
    else:
        yield target['endpoint'], {'filename': filename}, result['filePath']

def genericURLGenerator(target):
    """
        This yields `(endpoint, values)` tuples

        You can specify a different endpoint by yielding a (endpoint, values)
        tuple instead of just values, or you can by-pass
        url_for and simply yield URLs as strings.

        target is a dictionary
        {
            'rendererName': rendererName
          , 'config': targetConfig
          , 'endpoint': endpoint
          , 'indexEndpoint': indexEndpoint
          , 'feedEndpoint': feedEndpoint # may be None
          , 'suffix': suffix
          , 'source': source
          , 'pathparts': pathparts
        }
    """
    maxDepth = target['config'].get('maxdepth', float('inf'))
    if maxDepth == 0:
        return

    if 'source' in target:
        # target must define a source for this to happen
        # http://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
        source = '.' if target['source'] == '' else target['source']
        for root, dirs, files in os.walk(source):
            depth = root.count(os.path.sep) + 1 - source.count(os.path.sep)
            if depth >= maxDepth:
                # This is a the magic piece, it modifies the list that is
                # used by the os.walk iterator.
                # Deeper dirs won't be visited...
                del dirs[:]
            if depth > maxDepth:
                continue
            for filename in files:
                yield from fileURLGenerator(target, filename)
            for filename in target['config'].get('file_map', {}):
                yield from fileURLGenerator(target, filename, fromFileMap=True)
    else:
        # for the fileless_view, we could create more distinct conditions
        # here, but there's no need for this now
        yield target['endpoint'], {}, None

    feedEndpoint = target.get('feedEndpoint', None)
    if feedEndpoint:
        yield feedEndpoint, {}, None


class Menu(object):
    def __init__(self, app, targets):
        self._app = app
        self._targets = targets
        # we'll need this a lot but only need to generate it once
        links = self.allLinks([
                      target for target in targets
                                if target['config'].get('menu', True)]
                      # This currently skips the feed and fileless links,
                      # because they have no filePath
                    , includeFilePath=True)
        self._index = self._indexLinks(links)
        self._endpointIndex = self._indexTargets(targets)

    def _indexLinks(self, links):
        index = {}
        for endpoint, viewArgs, filePath in links:
            if endpoint not in index:
                index[endpoint] = {}
            viewArgsKey = frozenset(viewArgs.items())
            index[endpoint][viewArgsKey] = filePath
        return index

    def _indexTargets(self, targets):
        index = {}
        for target in targets:
            for key in ['endpoint', 'indexEndpoint', 'feedEndpoint']:
                endpoint = target.get(key, None)
                if endpoint is not None and endpoint in index:
                    raise ValueError('{0} "{1}" is not unique'.format(key, endpoint))
                index[endpoint] = target
        return index

    def _getLinkMetaData(self, endpoint, viewArgsKey, default=_defaultMarker):
        if endpoint not in self._index:
            if default is not _defaultMarker:
                return default
            raise KeyError('No endpoint "{0}"'.format(endpoint))
        if viewArgsKey not in self._index[endpoint]:
            if default is not _defaultMarker:
                return default
            raise KeyError('No entry in endpoint "{0}" for key "{1}"'.format(endpoint, viewArgsKey))
        filePath = self._index[endpoint][viewArgsKey]
        if filePath is not None:
            fileItem = self._app.config['fileDataCache'].get(filePath)
        else:
            fileItem = None
        return filePath, fileItem

    def _url_for(self, *args, **kwds):
        return self._app.jinja_env.globals['url_for'](*args, **kwds)

    def isActive(self, endpoint, viewArgs):
        return request.endpoint == endpoint and request.view_args == viewArgs

    def allLinks(self, targets=None, includeFilePath=False):
        if targets is None:
            targets = self._targets
        for target in targets:
            for endpoint, values, filePath in genericURLGenerator(target):
                if includeFilePath:
                    # filePath can be used to get (lazyly fetched and cached)
                    # metadata for the file
                    #if filePath is None:
                    #    # TODO: Currently the feed and the fileless endpoints
                    #    # don't have a filePath!
                    #    # But this is used to create menu entries. So, it
                    #    # should be possible to create links with this
                    #    # menu for these links.
                    #    continue
                    yield endpoint, values, filePath
                else:
                    yield endpoint, values

    def _getLinkName(self, endpoint, viewArgsKey, endpointName=None):
        meta = self._getLinkMetaData(endpoint, viewArgsKey)
        if meta is not None:
            filePath, fileItem = meta
            title = fileItem.setup.get('link_name', None) if fileItem else None
            if title is not None:
                return title

        target = self._endpointIndex[endpoint]
        if endpointName is None:
            endpointName = target['endpoint']
        if target.get('indexEndpoint', None) == endpoint:
            return target['config'].get('index_link_name', '{0}/'.format(endpointName))

        if target.get('feedEndpoint', None) == endpoint:
            pass
        elif 'source' in target:
            # indicates a filename using enpoint
            return '{0}/{1}'.format('' if endpoint == '__root__' else endpointName, dict(viewArgsKey).get('filename', ''))
        # feedEndpoint or fileless renderer
        return target['config'].get('link_name', '/' if endpoint == '__root__' else endpointName)


    def getLink(self, endpoint, include_meta=False, default=_defaultMarker, endpointName=None, **viewArgs):
        try:
            return self._getLink(endpoint, None, viewArgs, include_meta, endpointName=endpointName)
        except KeyError as e:
            if default is not _defaultMarker: return default
            raise e

    def _getFileItem(self, endpoint, viewArgsKey):
        _, fileItem = self._getLinkMetaData(request.endpoint, viewArgsKey, (None, None))
        return fileItem

    def getFileItem(self, endpoint, **viewArgs):
        viewArgsKey = frozenset(viewArgs.items())
        return self._getFileItem(endpoint, viewArgsKey)

    @property
    def fileItem(self):
        """ current file item """
        return self.getFileItem(request.endpoint, **request.view_args)

    @property
    def target(self):
        return self._endpointIndex[request.endpoint]

    @property
    def targets(self):
        return iter(sorted(self._targets, key=lambda target: target.get('endpoint', '')))

    def getAdjacentLinks(self, sortorder='default', reverse=False, include_meta=False):
        previous = current = after = last = None
        found = False
        for link in self.get([request.endpoint], sortorder=sortorder
                                , reverse=reverse, include_meta=True):
            meta = link[3]
            if found :
                after = link
                break
            elif meta['viewArgs'] == request.view_args:
                previous = last
                current = link
                found = True
                continue
            last = link
        if not include_meta:
            if previous: previous = tuple(previous[:-1])
            current = tuple(current[:-1])
            if after: after = tuple(after[:-1])
        return previous, current, after

    def _getLink(self, endpoint, viewArgsKey, viewArgs, include_meta, endpointName=None):
        if viewArgsKey is not None:
            # if both are not None, viewArgsKey wins
            viewArgs = dict(viewArgsKey)
        elif viewArgs is not None:
            viewArgsKey = frozenset(viewArgs.items())
        else:
            raise ValueError('One of viewArgsKey or viewArgs must be set.')

        name = self._getLinkName(endpoint, viewArgsKey, endpointName)
        url = self._url_for(endpoint, **viewArgs)
        active = self.isActive(endpoint, viewArgs)

        result = [url, name, active]
        if include_meta:
            (filePath, fileItem) = self._getLinkMetaData(endpoint, viewArgsKey, (None, None))
            result.append({
                'endpoint': endpoint
              , 'viewArgs': viewArgs
              , 'filePath': filePath
              , 'fileItem': fileItem
            })

        return tuple(result)

    def _sortName(self, linkdata):
        return self._getLinkName(*linkdata).lower()

    def _sortCTime(self,linkdata):
        filePath, fileItem = self._getLinkMetaData(*linkdata)
        return fileItem.times[0]

    def _sortMTime(self,linkdata):
        filePath, fileItem = self._getLinkMetaData(*linkdata)
        return fileItem.times[1]

    def _getSortKeyFunction(self, sortorder):
        return ({
            'name': self._sortName
          , 'ctime': self._sortCTime
          , 'mtime': self._sortMTime
        })[sortorder]

    def get(self, endpoints=None, sortorder='default', reverse=False, include_meta=False, endpointName=None):
        # todo: this should be more structured
        # all links of an endpoint should be yielded subsequently
        # and all links within an endpoint should be sorted (name->alphabet, ctime, mtime)

        if endpoints is None:
            endpoints = sorted(self._index.keys())

        for key in endpoints:

            endpoint = self._index.get(key, None)
            if endpoint is None:
                continue
            links = [(key, viewArgsKey) for viewArgsKey in endpoint.keys()]

            # determine how to sort
            if sortorder == 'default':
                target = self._endpointIndex[key]
                sortorder = target['config'].get('sortorder', 'name')
                reverse = target['config'].get('sortreverse', reverse)

            # sort
            if sortorder is not None:
                links = sorted(links, key=self._getSortKeyFunction(sortorder), reverse=reverse)
            elif reverse:
                links = reversed(links)

            for key, viewArgsKey in links:
                yield self._getLink(key, viewArgsKey, None, include_meta, endpointName=endpointName)

def deepListDir(destination):
    for root, dirs, files in os.walk(destination):
        for f in files:
            relpath = os.path.relpath(root, destination)
            yield f if relpath == '.' else os.path.join(relpath, f)

def makeFilesManifest(destination, fileName):
    out = StringIO()
    for f in deepListDir(destination):
        print(f, file=out)
    with open(os.path.join(destination, fileName), 'w') as f:
        f.write(out.getvalue())
    out.close()

def cleanDestination(destination, manifestFile):
    if not os.path.isdir(destination):
        return
    manifestPath = os.path.join(destination, manifestFile)
    if not os.path.isfile(manifestPath):
        return
    directories = set()

    with open(manifestPath, 'r') as manifest:
        for f in manifest:
            # If manifestFile was edited paths in it could be
            # outside of the destination dir.
            # We won't touch these.
            fileName = os.path.normpath(f.strip())
            if f.startswith('..'):
                continue
            dirname = os.path.dirname(fileName)
            if dirname and dirname != '.':
                directories.add(dirname)

            fileName = os.path.join(destination, fileName)
            try:
                os.remove(fileName)
            except FileNotFoundError:
                pass

    os.remove(manifestPath)
    fd_dir = os.open(destination, os.O_RDONLY)
    # try to remove the directories that we have touched
    # deletes only empty dirs
    deleted = set()
    for dirname in directories:
        while(dirname and dirname != '.'):
            if dirname in deleted:
                break
            try:
                os.rmdir(dirname, dir_fd=fd_dir)
                deleted.add(dirname)
            except OSError:
                pass
            dirname = os.path.dirname(dirname)

def generate(app, destination, manifestFile = '.webgenerator.manifest'):
    tempdir = tempfile.mkdtemp()
    try:
        _generate(app, tempdir)
        # we use this to clean up older versions of the generated page
        makeFilesManifest(tempdir, manifestFile)
        cleanDestination(destination, manifestFile)
        for f in deepListDir(tempdir):
            targetFile = os.path.join(destination, f)
            os.makedirs(os.path.dirname(targetFile), exist_ok=True)
            shutil.copy2(os.path.join(tempdir, f), targetFile)
    finally:
        shutil.rmtree(tempdir)


def _generate(app, destination):
    app.config.update(
        FREEZER_RELATIVE_URLS=True
      , FREEZER_DESTINATION=destination
    )

    freezer_config = app.config['generator_config'].get('freezer_config', None)
    if freezer_config:
        app.config.update(freezer_config)

    freezer = Freezer( app
                       # We'll have to request all pages manually. This
                       # way we can create some endpoints pro forma
                       # without yielding 404 errors.
                     , with_no_argument_rules=False)
    freezer.register_generator(app.config['menu'].allLinks)
    freezer.freeze()

def main(sourcepath, freezedir = None):
    app, menu = makeApp(sourcepath)

    @app.context_processor
    def inject_globals():
        return dict(
            menu=menu
          , dir=dir
        )
    if freezedir:
        generate(app, freezedir)
    else:
        app.run(debug=True)

if __name__ == '__main__':
    # the last argument sets sourcepath
    sourcepath = sys.argv[-1] if len(sys.argv) >= 2 else os.getcwd()
    destination = None
    # If there are 3 args, the second one sets a destination directory and
    # the website will be generated in there instead of running the development
    # server.
    if len(sys.argv) >= 3:
        destination = os.path.abspath(sys.argv[1])
    main(sourcepath, destination)

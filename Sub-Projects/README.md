```yaml
user_menu: False
docs_menu: True
link_name: Project
```

# Atem-Project is organized in sub-projects

The separation into Applications, Main Libraries and Basic/Helper Libraries is somewhat arbitrary, don't derive to much meaning from it.

{%- set listing = [
        ['Applications', None,
            [
                ['Metapolator', 'https://github.com/metapolator/metapolator', 'Design fonts and font families faster; Metapolator is the origin of Atem.', 'http://metapolator.com']
              , ['Atem-MOM-Developer-Tool', 'https://github.com/metapolator/Atem-MOM-Developer-Tool', 'Graphical inspection and manipulation of CPS and the Metapolator Object Model.', None]
              , ['Bauhaus-Emblem-Font', 'https://github.com/graphicore/Bauhaus-Emblem-Font', 'Technology demo, learning tool, next generation (type-)design Application, Inspiration.', None]
            ]
        ]
      , ['Main Libraries', 'The building blocks for Atem-Applications.',
            [
                ['ufoJS', 'https://github.com/graphicore/ufoJS/', 'Javascript API for the **U**nified **F**ont **O**bject.', 'http://lib.ufojs.org']
              , ['Atem-IO', 'https://github.com/graphicore/Atem-IO', 'Simple, unified input/outout API for JavaScript. Includes API adapters and tools.', None]
              , ['Atem-Pen-Case', 'https://github.com/graphicore/Atem-Pen-Case', 'JavaScript API-implementation of the Segment-Pen-Protocol and Point-Pen-Protocol plus a collection of pens.', None]
              , ['Atem-Property-Language', 'https://github.com/graphicore/Atem-Property-Language', 'Language to define CPS property values; includes the formulae language of Atem-MOM.', None]
              , ['Atem-CPS', 'https://github.com/graphicore/Atem-CPS', 'CPS—**C**ascading **P**roperties **S**heets and OMA—**O**bject **M**odel **A**PI', None]
              , ['Atem-MOM', 'https://github.com/graphicore/Atem-MOM', 'MOM—**M**etapolator **O**bject **M**odel', None]
              , ['obtainJS', 'https://github.com/graphicore/obtainJS', 'Framework to unify synchronous and asynchronous JavaScript.', None]
              , ['Atem-CPS-Developer-Tool', 'https://github.com/graphicore/Atem-CPS-Developer-Tool', 'Graphical user interface tools for CPS and the OMA on a generic level. (currently uses just as library not as application)', None]
              , ['Atem-CPS-Toolkit', 'https://github.com/graphicore/Atem-CPS-Toolkit', 'Shared tools used to render the CPS/OMA in user interfaces.', None]
              , ['Atem-MOM-Toolkit', 'https://github.com/graphicore/Atem-MOM-Toolkit', 'Shared tools used to render the Metapolator Object Model in user interfaces.', None]
            ]
        ]
      , ['Basic/Helper Libraries', 'These are libraries and tools that are used throughout many of the Atem projects more infrastructure than innovation.',
            [
                ['Atem-Errors', 'https://github.com/graphicore/Atem-Errors', 'Library commonly used by Atem-Project for Error-Class creation.', None]
              , ['Atem-CPS-whitelisting', 'https://github.com/graphicore/Atem-CPS-whitelisting', 'Atem Project: lightweight dependency to prepare objects for usage within Atem-CPS; whitelisting accessible properties.', None]
              , ['Atem-Math-Tools', 'https://github.com/graphicore/Atem-Math-Tools', 'Collection of (2d graphics) math modules used in Atem.', None]
              , ['Atem-RequireJS-Config', 'https://github.com/graphicore/Atem-RequireJS-Config/', 'common RequireJS configuration for all Atem sub-projects.', None]
              , ['Atem-Logging', 'https://github.com/graphicore/ Atem-Logging', 'Versatile logging facility based on util-logging adding some specifics for Atem.', None]
            ]
        ]
    ]
-%}

{% for name, sub, items in listing %}
### {{name}}
{% if sub -%}{{ sub }}{%- endif %}

{% for item, link, desc, web in items -%}
* <a href="{{link}}" target="_blank" title="on GitHub">{{item}}</a> {{desc}}
        {%- if web %}<a href="{{web}}" target="_blank">(website)</a>{% endif %}
{% endfor -%}
{% endfor %}


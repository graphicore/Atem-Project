```yaml
title: News
template: standard.html
```
# {{feed_title}}

**Follow [@AtemProject](https://twitter.com/AtemProject)**

{% from 'lib.html' import render_news_links with context %}
<ol>{{ render_news_links()|safe}}</ol>

Use a newsreader? Here's our [Atom Feed]({{url_for('news.feed')}})

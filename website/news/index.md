```yaml
title: News
template: standard.html
```
# {{feed_title}}

This is a growing list of project news posts.

**Stay up-to-date.** Subscribe to the [news feed]({{url_for('news.feed')}}) or follow [@AtemProject](https://twitter.com/AtemProject) on Twitter.

{% from 'lib.html' import render_news_links with context %}
<ol>{{ render_news_links()|safe}}</ol>


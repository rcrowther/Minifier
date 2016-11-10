Minifier
=========
Script-like Python-GTK interface for minifying CSS and JS.

.. figure:: https://raw.githubusercontent.com/rcrowther/Minifier/master/text/minifier.jpg
    :width: 160 px
    :alt: Minifier screenshot
    :align: center

    Only when the moon wanes


Why?
~~~~~
Those online compressors are more of a demonstration of web-building than a useful tool. This is more of a useful tool than a demonstration of web-building. It assumes you have a website (development/staging, whatever) and need to sometimes minify files. Lists directory contents, so you can select files.

Can use the Java YUI compressor, available separately. Not the last word in compression, but at least you know how it works. Can also use the Python Slimmer compressor, available in Debian repositories. Rather than arguing which is better, the choice will usually be a case of language dependency. If your environment uses Java, use YUI. If not, the last thing you want is a Java dependency (for a minifier), so use Slimmer.

Useful info at
https://webassets.readthedocs.io/en/latest/builtin_filters.html#css-compressors


Requires
~~~~~~~~
YUI compressor executable, or 'python3-slimmer' package install. Python3, GTK environment, and some setup. Instructions included.


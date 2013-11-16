serve:
	python -m SimpleHTTPServer

notebook:
	ipython notebook --pylab --notebook-dir=experiments

push:
	-git branch -D gh-pages
	git checkout -b gh-pages
	git push -f -u origin gh-pages
	git checkout master

.PHONY: serve

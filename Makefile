ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

update-frontend:
	-test ! -d client && git clone https://github.com/elastic/opbeans-frontend client
	cd client && git pull

compile-frontend:
	cd client && npm --no-bin-links install && npm run-script build
	rm -rf $(ROOT_DIR)/opbeans/static && \
	    mkdir -p $(ROOT_DIR)/opbeans/static/build && \
	    cp -r $(ROOT_DIR)/client/build/* $(ROOT_DIR)/opbeans/static/build && \
	    cp -r $(ROOT_DIR)/client/package.json $(ROOT_DIR)/opbeans/static/
	sed 's/<head>/<head>{% block head %}{% endblock %}/' $(ROOT_DIR)/client/build/index.html | sed 's/<script type="text\/javascript" src="\/rum-config.js"><\/script>//' > $(ROOT_DIR)/opbeans/templates/base.html

frontend: | update-frontend compile-frontend

.PHONY: frontend update-frontend compile-frontend push-image

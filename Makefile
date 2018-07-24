ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

update-frontend:
	-test ! -d client && git clone https://github.com/elastic/opbeans-frontend client
	cd client && git pull

compile-frontend:
	cd client && npm install && npm run-script build
	-test ! -L opbeans/static/build && ln -s $(ROOT_DIR)/client/build $(ROOT_DIR)/opbeans/static/build
	-test ! -L opbeans/templates/index.html && ln -s $(ROOT_DIR)/client/build/index.html $(ROOT_DIR)/opbeans/templates/index.html

frontend: | update-frontend compile-frontend

.PHONY: frontend update-frontend compile-frontend push-image

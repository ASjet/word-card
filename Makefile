.PHONY: run build clean
run:
	cd build && python main.py

build: .NPM_INSTALL
	rm -rf build
	npm run build
	cp app/* build/
	mkdir build/templates
	mv build/index.html build/templates

.NPM_INSTALL: package.json
	npm install
	touch .NPM_INSTALL

clean:
	rm -rf build

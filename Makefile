.PHONY: run build clean
run:
	cd build && python main.py

build: .NPM_INSTALL
	npm run build
	cp app/* build/
	mkdir -p build/templates
	mv build/index.html build/templates

.NPM_INSTALL: package.json
	npm install
	touch .NPM_INSTALL

clean:
	rm -rf build

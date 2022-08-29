TIMESTAMP=$(shell date "+%Y%m%dT%H%M%S")
DUMP_NAME=db_dump_$(TIMESTAMP)

.PHONY: run build build-back dump purge clean
run:
	@cd build && python main.py

build: .NPM_INSTALL
	@rm -rf build
	@npm run build
	@-cp app/*.py build/
	@-cp .env build/
	@mkdir build/templates
	@mv build/index.html build/templates

build-back:
	@-cp app/*.py build/
	@-cp .env build/

.NPM_INSTALL: package.json
	@npm install
	@touch .NPM_INSTALL

dump:
	@cd app/ && python main.py -d ../$(DUMP_NAME)
	@tar -vczf $(DUMP_NAME).tar.gz $(DUMP_NAME)/
	@mkdir -p dumps/
	@mv $(DUMP_NAME).tar.gz dumps/
	@rm -rf $(DUMP_NAME)/
#
migrate:
	@cd app/ && python main.py -m ../records -v

purge:
	@rm words.db

clean:
	@rm -vrf build .NPM_INSTALL

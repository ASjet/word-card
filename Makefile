TIMESTAMP=$(shell date "+%Y%m%dT%H%M%S")
DUMP_NAME=db_dump_$(TIMESTAMP)

.PHONY: run build build-back dump purge clean
run:
	@cd build && python main.py

build_npm: .NPM_INSTALL
	@cd ./src/assets && npm run build

build:
	cd ./src && go build -o ../release/wordcard ./cmd

.NPM_INSTALL: package.json
	@cd ./src/assets && npm install
	@touch .NPM_INSTALL

purge:
	@rm words.db

clean:
	@rm -vrf ./src/assets/.NPM_INSTALL release/wordcard

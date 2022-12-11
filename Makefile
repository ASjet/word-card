.PHONY: build purge clean
build:
	cd ./src && go build -ldflags '-linkmode "external" -extldflags "-static"' -o ../release/wordcard ./cmd

build_npm: .NPM_INSTALL
	@cd ./src/assets && npm run build

.NPM_INSTALL: package.json
	@cd ./src/assets && npm install
	@touch .NPM_INSTALL

purge:
	@rm words.db

clean:
	@rm -vrf ./src/assets/.NPM_INSTALL release/wordcard

# word-card

[![License](https://img.shields.io/github/license/ASjet/word-card)](https://github.com/ASjet/word-card/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/ASjet/word-card)](https://github.com/ASjet/word-card/releases/latest)


Memorize words in context

## API

Use [OxfordDictionaries](https://developer.oxforddictionaries.com/) as dictionary api service, read [documentation](https://developer.oxforddictionaries.com/documentation) for more information.

## Usage

### Build

Build and setup

```shell
make build
```

### Run

Start `Flask` server

```shell
make run
```

### Dump

Dump database to `dumps/` in json format, one file per record

```shell
make dump
```

### Migrate

Load record in json from `records/`, one record per file

```shell
make migrate
```

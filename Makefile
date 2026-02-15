SIEVE_DB ?= /home/kellogg/data/sieve.db
HUGO ?= $(HOME)/.local/bin/hugo

.PHONY: build export serve clean

build: export
	mkdir -p static/data
	cp data/articles.json static/data/articles.json
	$(HUGO) --minify

export:
	python3 scripts/export.py --sieve-db $(SIEVE_DB) --output .

serve: export
	mkdir -p static/data
	cp data/articles.json static/data/articles.json
	$(HUGO) server --buildDrafts

clean:
	rm -rf public/ resources/

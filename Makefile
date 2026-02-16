SIEVE_DB ?= /home/kellogg/data/sieve.db
HUGO ?= $(HOME)/.local/bin/hugo
VPS_HOST ?= kellogg@147.182.199.226
VPS_PATH ?= /var/www/rogueroutine.brengel.com

.PHONY: build export serve clean deploy

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

deploy: build
	rsync -avz --delete public/ $(VPS_HOST):$(VPS_PATH)/
	@echo "Deployed to $(VPS_HOST):$(VPS_PATH)"

clean:
	rm -rf public/ resources/

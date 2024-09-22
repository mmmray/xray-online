build: main.wasm wasm_exec.js xray.schema.json
.PHONY: build

dev-lite:
	wget -nc https://mmmray.github.io/xray-online/main.wasm
	wget -nc https://mmmray.github.io/xray-online/wasm_exec.js
.PHONY: build-lite

assets/xray-patched: xray-version.txt
	rm -rf assets/xray-core assets/xray-patched
	mkdir -p assets
	cd assets && \
		git clone https://github.com/xtls/xray-core && \
		cd xray-core && \
		git checkout -f $$(cat ../../xray-version.txt)
	cat xray-wasm.patch | (cd assets/xray-core && git apply)
	mv assets/xray-core assets/xray-patched

assets/geoip.dat:
	mkdir -p assets
	cd assets && wget https://github.com/v2fly/geoip/releases/latest/download/geoip.dat

assets/geosite.dat:
	mkdir -p assets
	cd assets && wget https://github.com/v2fly/domain-list-community/releases/latest/download/dlc.dat -O geosite.dat

wasm_exec.js:
	cp "$$(go env GOROOT)/misc/wasm/wasm_exec.js" .

main.wasm: assets/geoip.dat assets/geosite.dat assets/xray-patched main.go go.mod xray-wasm.patch
	GOARCH=wasm GOOS=js go build -o main.wasm main.go

xray.schema.json: scrape-docs.py
	rm -rf assets/xray-docs-next
	mkdir -p assets
	cd assets && git clone --depth 1 https://github.com/xtls/xray-docs-next
	grep -r '' assets/xray-docs-next/docs/en/config/ | cut -d: -f2- | python3 scrape-docs.py > xray.schema.json


serve:
	python3 -mhttp.server

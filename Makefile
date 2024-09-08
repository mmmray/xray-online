geoip.dat:
	wget https://github.com/v2fly/geoip/releases/latest/download/geoip.dat

geosite.dat:
	wget https://github.com/v2fly/domain-list-community/releases/latest/download/dlc.dat -O geosite.dat

build: geoip.dat geosite.dat
	cp "$$(go env GOROOT)/misc/wasm/wasm_exec.js" .
	GOARCH=wasm GOOS=js go build -o main.wasm main.go

serve:
	python3 -mhttp.server

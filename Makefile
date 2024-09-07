build:
	cp "$$(go env GOROOT)/misc/wasm/wasm_exec.js" .
	GOARCH=wasm GOOS=js go build -o main.wasm

serve:
	python3 -mhttp.server

package main

import (
    "fmt"
    "syscall/js"
	"encoding/json"
	"bytes"

	"github.com/xtls/xray-core/infra/conf"
	json_reader "github.com/xtls/xray-core/infra/conf/json"
)

func main() {
    js.Global().Set("XrayParseConfig", js.FuncOf(func(this js.Value, args []js.Value) any {
        if len(args) < 1 {
            fmt.Println("invalid number of args")
            return nil
        }

        arg := args[0]
        if arg.Type() != js.TypeString {
            fmt.Println("the argument should be a string")
            return nil
        }

		jsonConfig := &conf.Config{}
		jsonReader := &json_reader.Reader{
			Reader: bytes.NewReader([]byte(arg.String())),
		}
		decoder := json.NewDecoder(jsonReader)

		if err := decoder.Decode(jsonConfig); err != nil {
			return err.Error()
		}

		return nil
    }))

    // Prevent the program from exiting.
    // Note: the exported func should be released if you don't need it any more,
    // and let the program exit after then. To simplify this demo, this is
    // omitted. See https://pkg.go.dev/syscall/js#Func.Release for more information.
    select {}
}

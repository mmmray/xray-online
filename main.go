package main

import (
    "fmt"
	"strings"
    "syscall/js"
	"encoding/json"
	"bytes"
	"io"
	_ "embed"
	"io/ioutil"

	"github.com/xtls/xray-core/infra/conf"
	"github.com/xtls/xray-core/common/platform/filesystem"
	"github.com/xtls/xray-core/common/errors"
	json_reader "github.com/xtls/xray-core/infra/conf/json"
)

//go:embed geoip.dat
var geoipRaw []byte
//go:embed geosite.dat
var geositeRaw []byte

func main() {
	filesystem.NewFileReader = func(path string) (io.ReadCloser, error) {
		if strings.HasSuffix(path, "geoip.dat") {
			return ioutil.NopCloser(bytes.NewReader(geoipRaw)), nil
		}

		if strings.HasSuffix(path, "geosite.dat") {
			return ioutil.NopCloser(bytes.NewReader(geositeRaw)), nil
		}

		return nil, errors.New(path + " cannot be opened in the browser")
	}

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

		if _, err := jsonConfig.Build(); err != nil {
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

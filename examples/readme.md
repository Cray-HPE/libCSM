# Examples for how one might use this library of shenanigans

## `cmdhook.sh`

This example script exists to demonstrate how a user could write their own hooks that could be called via the `cmdhook` wrapper generation function.

The intent is to make output like this:

```bash
./examples/cmdhook.sh
```

Output:
```text
curl: (1) Protocol "uri" not supported or disabled in libcurl
parse error: Invalid numeric literal at line 1, column 10
ls: cannot access '/does/not/exist': No such file or directory
rm: cannot remove '/does/not/exist': No such file or directory
zsh: exit 1     ./examples/cmdhook.sh
```

More useful when one uses the `wrapcmd` hook functions and wrap a command as called in shell. Example:

```bash
WRAP="jq" DEBUG=sure ./examples/cmdhook.sh
```

Output:

```text
curl: (1) Protocol "uri" not supported or disabled in libcurl
default cmdhook debug begin

command: /Users/user/.nix-profile/bin/jq -r .
rc: 0
pwd: /Users/user/src/wrk/github.com/Cray-HPE/csm-common-library
stdin /private/var/folders/pt/tg8xf0mx0j5_cp2m4hn_8qnc0000gn/T/csm-common-lib-50221/stdin-is-a-pipe-Hvz3faOQ: file is empty no data present
stdout /private/var/folders/pt/tg8xf0mx0j5_cp2m4hn_8qnc0000gn/T/csm-common-lib-50221/stdout-Qz6eFzRy: file is empty no data present
stderr /private/var/folders/pt/tg8xf0mx0j5_cp2m4hn_8qnc0000gn/T/csm-common-lib-50221/stderr-0uTyt2A6: file is empty no data present

default cmdhook debug end
parse error: Invalid numeric literal at line 1, column 10
default cmdhook debug begin

command: /Users/user/.nix-profile/bin/jq -r .
rc: 4
pwd: /Users/user/src/wrk/github.com/Cray-HPE/csm-common-library
stdin /private/var/folders/pt/tg8xf0mx0j5_cp2m4hn_8qnc0000gn/T/csm-common-lib-50221/stdin-is-a-pipe-rNqdWqhQ:
<!doctype html>
<html>
<head>
    <title>Example Domain</title>

    <meta charset="utf-8" />
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style type="text/css">
    body {
        background-color: #f0f0f2;
        margin: 0;
        padding: 0;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;

    }
    div {
        width: 600px;
        margin: 5em auto;
        padding: 2em;
        background-color: #fdfdff;
        border-radius: 0.5em;
        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);
    }
    a:link, a:visited {
        color: #38488f;
        text-decoration: none;
    }
    @media (max-width: 700px) {
        div {
            margin: 0 auto;
            width: auto;
        }
    }
    </style>
</head>

<body>
<div>
    <h1>Example Domain</h1>
    <p>This domain is for use in illustrative examples in documents. You may use this
    domain in literature without prior coordination or asking for permission.</p>
    <p><a href="https://www.iana.org/domains/example">More information...</a></p>
</div>
</body>
</html>
stdout /private/var/folders/pt/tg8xf0mx0j5_cp2m4hn_8qnc0000gn/T/csm-common-lib-50221/stdout-If20mxl7: file is empty no data present
stderr /private/var/folders/pt/tg8xf0mx0j5_cp2m4hn_8qnc0000gn/T/csm-common-lib-50221/stderr-uo4OUMsi:
parse error: Invalid numeric literal at line 1, column 10

default cmdhook debug end
ls: cannot access '/does/not/exist': No such file or directory
rm: cannot remove '/does/not/exist': No such file or directory
zsh: exit 1     WRAP="jq" DEBUG=sure ./examples/cmdhook.sh
```

As one can see one will receive information one wouldn't get by default, or with `set -x` either. Specifically:

- What was `stdin` to the command, if it was provided as a pipe
- What was the commands `stdout`, if it was provided or output to a pipe
- What was the commands `stderr`, if it was provided or output to a pipe
- What was the commands working directory
- What was the commands return code
- What was the full path to the command and its args

> Note that hooks of any complexity could be conceived, but the intent here is to provide a
> drop-in solution to help debug existing scripts without rewriting all of them logic wise.

This example script provides an example of writing one's own non default hook for the wrapper trampoline function that is created. One could imagine saving all this data in a timeline sequence to record all command executions, timing data etc...

For now the default hook should provide enough information to debug any existing command reasonably well.

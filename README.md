# power-pusher

After installing, the cli can be run like:

```sh
power-pusher power-on --index 0
```

for "pushing" the power button with the first output.

# Help:

```
$ power-pusher --help
Usage: power-pusher [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level <LAMBDA>
  --help                Show this message and exit.

Commands:
  power-hold
  power-off
  power-on
```

```
$ power-pusher power-hold --help
Usage: power-pusher power-hold [OPTIONS]

Options:
  --index INTEGER       index for which to hold power  [required]
  --hold-seconds FLOAT  how many seconds to "hold the power button down"
                        [required]
  --help                Show this message and exit.
```

```
$ power-pusher power-off --help
Usage: power-pusher power-off [OPTIONS]

Options:
  --index INTEGER       index for which to hold power  [required]
  --hold-seconds FLOAT  how many seconds to "hold the power button down"
  --help                Show this message and exit.
```

```
$ power-pusher power-on --help
Usage: power-pusher power-on [OPTIONS]

Options:
  --index INTEGER       index for which to hold power  [required]
  --hold-seconds FLOAT  how many seconds to "hold the power button down"
  --help                Show this message and exit.
```

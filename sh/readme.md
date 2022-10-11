# Shell library docs

## Rough design plan (not yet fully implemented)

Premise here is if you want the whole hog just source *sh/lib.sh* after setting SOURCEPREFIX to the directory containing that dir/file. For posix shells there is no way to portably "know" where you were imported from, so we just defer that to calling scripts as they can know where they're importing from.

When you have that you get all the fun stuff.

Eventual goal:
- Make debugging shell a bit easier and have some standard library of shell to aide in our usage

That will end up with something like scripts having:

```sh
SOURCEPREFIX=$CWD source ./sh/lib.sh

wrapcmd ls ps curl jq

... stuff
```

And when called with *DEBUG=anyvalue* and/or *TIMELINE=anyvalue* you will end up with a directory of say */tmp/PARENTPID* with dirs of the epoch start time of any ls, ps, curl or jq call containing:
- cmdline: The command line of what was called
- rc: The return code it exited with
- stdin{-is-a-pipe}: Standard input, and if it was a pipe the filename will reflect that
- stdout{-is-a-pipe}: Standard output, and if it was a pipe the filename will reflect that
- stderr{-is-a-pipe}: Standard error, and if it was a pipe the filename will reflect that

That will help with debugging shell scripts that utilize the wrapper functions.

In a near future commit default hooks for the wrapper functions generated will help in output to the screen. For now this is MVP status. An example hook is located in the examples directory at the base of this repo.

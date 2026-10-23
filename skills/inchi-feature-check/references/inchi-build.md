# Building and testing InChI without touching the user's checkout

The user's `../InChI` clone has their branch and their build directories. Work in a
detached worktree in the session's scratch folder (`$SCRATCH` below) and remove it at
the end.

```
git -C ../InChI fetch -q origin
git -C ../InChI worktree add --detach $SCRATCH/inchi-<rev> <rev>
W=$SCRATCH/inchi-<rev>
```

## Unit tests (C/C++, GoogleTest)

Build in `<worktree>/CMake_build/full_build`, not elsewhere: on branches without the
`FIXTURES_DIR` CMake define, some suites (`test_enhancedStereo`, `test_ichimain`) open
fixtures through a fixed `../../../../../` path that only resolves from there, and fail
falsely in any other build directory.

```
cmake -S $W -B $W/CMake_build/full_build -DCMAKE_BUILD_TYPE=Release
cmake --build $W/CMake_build/full_build -j
(cd $W/CMake_build/full_build && ctest -j --output-on-failure)
```

One suite or test: run its binary under `INCHI-1-TEST/tests/test_unit/` in the build
directory with `--gtest_filter='*name*'`; `--gtest_list_tests` counts tests for a spec.

## Executable tests (Python, pytest)

```
python3 -m venv $SCRATCH/pytest-venv && $SCRATCH/pytest-venv/bin/pip install -q pytest
$SCRATCH/pytest-venv/bin/pytest $W/INCHI-1-TEST/tests/test_executable -q
```

They need the CLI built; see the README in `INCHI-1-TEST/` for the binary path they
expect.

## CLI only (to measure strings)

```
cmake -S $W/INCHI-1-SRC/INCHI_EXE/inchi-1/src -B $W/cli -DCMAKE_BUILD_TYPE=Release
cmake --build $W/cli -j      # -> $W/cli/bin/inchi-1
$W/cli/bin/inchi-1 file.mol -STDIO -NoLabels -AuxNone [-Key] [options]
```

`tools/rebuild.py` keeps such binaries per revision in `~/.cache/inchi-specs/<commit>/`;
reuse them for measuring.

## Clean up

```
git -C ../InChI worktree remove --force $W
```

# wkhtmltopdf buildpack

A classic buildpack for Heroku-24 and Dokku Herokuish. It installs
wkhtmltopdf, runtime libraries, and fonts inside the app directory.
It does not require root or change system packages.

## Use

Add an empty `.wkhtmltopdf-buildpack` file to your app. In `.buildpacks`,
list this buildpack before your language buildpack:

```
https://github.com/khanlou/heroku-buildpack-wkhtmltopdf#FULL_COMMIT_SHA
```

Replace `FULL_COMMIT_SHA` with a tested commit. The runtime profile sets
`WKHTMLTOPDF_PATH` to `$HOME/.wkhtmltopdf/bin/wkhtmltopdf`. Your app must use
that path. If profiles are not loaded, invoke the wrapper directly.

The wrapper sets library and font paths for its child process. It can be
moved with the app. It does not install a binary in `/usr/local/bin`.

## Requirements and packages

- Ubuntu 24.04, Linux amd64, `STACK=heroku-24`.
- Build tools: Bash, curl, APT, dpkg-deb, sha256sum, ldd, and the Ubuntu
  archive keyring. These are supplied by the Herokuish 24 build image.
- At least 512 MiB free for this buildpack's temporary files and output.
  Container images and language builds require additional space.

The binary is wkhtmltopdf 0.12.6.1 with patched Qt, from the official
`0.12.6.1-3.jammy_amd64` package. It uses OpenSSL 3. Other stacks and
architectures are rejected.
Only the PDF executable is retained; wkhtmltoimage and the C API library
are not included.

The package is downloaded over HTTPS and checked against this SHA-256:

```
4f723b2691ad8638a9df960e0421d346d7315083e3583a334f33362280ddba15
```

The hash was calculated from the upstream release download. Upstream does
not publish a signature for this asset. The archive is cached and checked
on each build. A corrupt cache causes a build failure.

Libraries and fonts use current Noble packages from signed Ubuntu indexes.
APT verifies repository signatures and package hashes. The buildpack extracts
packages without running installation scripts. Exact package versions and
hashes are recorded in `.wkhtmltopdf/packages.tsv` and `packages.sha256`.
The stack supplies glibc and the ELF loader.

Fonts include DejaVu, Liberation, URW Base35, X base fonts, and X 75 dpi fonts. Generic
font families map to DejaVu. Arial/Helvetica, Times New Roman, and Courier New
map to Liberation. Full CJK and emoji coverage is not included.

## Manual test

Use a clean Herokuish 24 container without a system wkhtmltopdf installation.

```sh
mkdir -p test-output/app test-output/cache test-output/env test-output/results
touch test-output/app/.wkhtmltopdf-buildpack
STACK=heroku-24 bin/compile test-output/app test-output/cache test-output/env
test/smoke test-output/app test-output/results
python3 test/verify-pdfs.py
```

The last command requires Poppler's `pdfinfo`, `pdftotext`, `pdffonts`, and
`pdftoppm`. The test checks version and license output, bundled font paths,
Letter-size PDF output, Latin accents, Greek, Cyrillic, and embedded fonts.
It also checks that all libraries except glibc and its loader come from the
bundle. An existing image can be used if its system renderer is hidden in
the test container; system libraries and fonts cannot mask missing bundle files.
Inspect `test-output/results/preview.png` for visual layout.

## Limitations

wkhtmltopdf is no longer maintained. Use trusted HTML and URLs. Version
0.12.6 blocks local resources by default; pass `--enable-local-file-access`
only when your application requires and permits it. Rendering can differ
from earlier versions. Check representative documents before an upgrade.

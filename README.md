# Font Converter

A simple CLI tool for converting font files between TTF, OTF, WOFF, and WOFF2 formats. Supports both single file and batch directory conversion.

## Installation

### Option 1: Direct install
```bash
pip3 install fonttools brotli cu2qu
```

### Option 2: Using requirements.txt
```bash
pip3 install -r requirements.txt
```

- `brotli` is required for WOFF2 support
- `cu2qu` is required for OTF → TTF outline conversion (optional, works without it)

## Usage

### Single file conversion

```bash
# Basic (creates new file in the same directory)
python3 fc.py -f font.ttf -t woff

# Specify output file
python3 fc.py -f font.ttf -o mynewfont.woff -t woff
```

### Batch directory conversion

```bash
# Convert in place (skips files already in target format)
python3 fc.py -d ./fonts -t woff2

# Output to different directory
python3 fc.py -d ./fonts -o ./converted -t woff2
```

### Overwriting existing files

By default, existing files/directories are not overwritten. Use `--force` to override.

```bash
python3 fc.py -f font.ttf -o existing.woff -t woff --force
python3 fc.py -d ./fonts -o ./existing_folder -t woff2 --force
```

## Options

| Option | Description |
|--------|-------------|
| `-f, --file` | Single file to convert |
| `-d, --directory` | Directory to convert (recursive) |
| `-o, --output` | Output file/directory path |
| `-t, --target` | Target format: `ttf`, `woff`, or `woff2` |
| `--force` | Overwrite existing files |

## Notes

- **OTF → TTF conversion**: With `cu2qu` installed, CFF outlines are converted to TrueType outlines. Without it, only the extension changes.
- Mixed-case extensions (e.g., `.TtF`) are recognized automatically.
- Input and output directories cannot be the same.

## Examples

```bash
# Convert all Noto Sans fonts to WOFF2
python3 fc.py -d Noto_Sans -o Noto_Sans_woff2 -t woff2

# Convert a single file
python3 fc.py -f NotoSans-Regular.ttf -t woff

# Force overwrite existing directory
python3 fc.py -d fonts/ -o output/ -t woff --force
```

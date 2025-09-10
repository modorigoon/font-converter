#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from fontTools.ttLib import TTFont
try:
    from fontTools.cu2qu import fonts_to_quadratic
    CU2QU_AVAILABLE = True
except ImportError:
    fonts_to_quadratic = None
    CU2QU_AVAILABLE = False


def get_font_format(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)

        if header[:4] == b'\x00\x01\x00\x00' or header[:4] == b'true' or header[:4] == b'typ1':
            return 'ttf'
        elif header[:4] == b'OTTO':
            return 'otf'
        elif header[:4] == b'wOFF':
            return 'woff'
        elif header[:4] == b'wOF2':
            return 'woff2'
        else:
            font = TTFont(file_path)
            try:
                if font.flavor == 'woff':
                    return 'woff'
                elif font.flavor == 'woff2':
                    return 'woff2'
                else:
                    return 'ttf'
            finally:
                font.close()
    except (OSError, IOError):
        return None


def convert_cff_to_true_type(font):
    if not CU2QU_AVAILABLE or not callable(fonts_to_quadratic):
        return False
    
    try:
        if 'CFF ' not in font and 'CFF2' not in font:
            return True

        fonts_to_quadratic([font])
        return True
    except (ValueError, TypeError):
        return False


def convert_font(input_path, output_path, target_format):
    try:
        font = TTFont(input_path)

        source_format = get_font_format(input_path)
        if source_format == 'otf' and target_format == 'ttf':
            if convert_cff_to_true_type(font):
                print("  → Converted CFF outlines to TrueType outlines")
            else:
                print("  → Warning: Could not convert outlines, keeping CFF format", file=sys.stderr)

        if target_format == 'woff':
            font.flavor = 'woff'
        elif target_format == 'woff2':
            font.flavor = 'woff2'
        elif target_format == 'ttf':
            font.flavor = None

        font.save(output_path)
        font.close()
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}", file=sys.stderr)
        return False


def validate_input_file(input_file):
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' does not exist", file=sys.stderr)
        return None
    
    source_format = get_font_format(input_file)
    if not source_format:
        print(f"Error: Unable to detect format of '{input_file}'", file=sys.stderr)
        return None
    
    return source_format


def check_otf_conversion(source_format, target_format):
    if source_format == 'otf' and target_format == 'ttf':
        if CU2QU_AVAILABLE:
            print("Note: Converting OTF to TTF with outline conversion (CFF → TrueType).", file=sys.stderr)
        else:
            print("Note: Converting OTF (CFF outlines) to .ttf extension. Install 'cu2qu' for outline conversion.", file=sys.stderr)


def determine_output_path(args, input_file):
    if args.output:
        output_file = Path(args.output)
        if output_file.exists() and output_file.is_dir():
            print(f"Error: Output path '{output_file}' is an existing directory", file=sys.stderr)
            return None
        
        if output_file.exists() and not args.force:
            print(f"Error: Output file '{output_file}' already exists. Use --force to overwrite.", file=sys.stderr)
            return None
    else:
        output_file = input_file.with_suffix(f'.{args.target}')
        if output_file.exists() and output_file != input_file and not args.force:
            print(f"Error: Output file '{output_file}' already exists. Use --force to overwrite.", file=sys.stderr)
            return None
    
    return output_file


def process_single_file(args):
    input_file = Path(args.file)
    source_format = validate_input_file(input_file)
    if not source_format:
        return False

    if source_format == args.target:
        print(f"Skipping: Source and target formats are the same ({args.target})", file=sys.stderr)
        return True

    check_otf_conversion(source_format, args.target)

    output_file = determine_output_path(args, input_file)
    if not output_file:
        return False

    output_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"Converting: {input_file} -> {output_file}")
    return convert_font(input_file, output_file, args.target)


def validate_directory(input_dir, output_dir=None):
    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist", file=sys.stderr)
        return False
    
    if not input_dir.is_dir():
        print(f"Error: '{input_dir}' is not a directory", file=sys.stderr)
        return False
    
    if output_dir and input_dir.resolve() == output_dir.resolve():
        print("Error: Input and output directories cannot be the same", file=sys.stderr)
        return False
    
    return True


def find_font_files(input_dir):
    font_extensions = {'.ttf', '.otf', '.woff', '.woff2'}
    font_files = []

    for file_path in input_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in font_extensions:
            font_files.append(file_path)
    
    return font_files


def convert_directory_file(font_file, input_dir, output_dir, target_format, has_output):
    relative_path = font_file.relative_to(input_dir)

    if has_output:
        output_file = output_dir / relative_path.with_suffix(f'.{target_format}')
    else:
        output_file = font_file.with_suffix(f'.{target_format}')

    source_format = get_font_format(font_file)
    if not source_format:
        print(f"Warning: Unable to detect format of '{font_file}', skipping", file=sys.stderr)
        return 0

    if has_output:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        print(f"Converting: {font_file} -> {output_file}")
        return 1 if convert_font(font_file, output_file, target_format) else -1
    else:
        if source_format == target_format:
            print(f"Skipping: {font_file} (already in {target_format} format)", file=sys.stderr)
            return 0

        print(f"Converting: {font_file} -> {output_file}")
        return 1 if convert_font(font_file, output_file, target_format) else -1


def process_directory(args):
    input_dir = Path(args.directory)
    output_dir = Path(args.output) if args.output else input_dir

    if not validate_directory(input_dir, output_dir if args.output else None):
        return False

    if args.output and output_dir.exists() and not args.force:
        print(f"Error: Output directory '{output_dir}' already exists. Use --force to overwrite.", file=sys.stderr)
        return False

    font_files = find_font_files(input_dir)
    if not font_files:
        print(f"No font files found in '{input_dir}'", file=sys.stderr)
        return True

    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for font_file in font_files:
        result = convert_directory_file(font_file, input_dir, output_dir, args.target, bool(args.output))
        if result == 1:
            success_count += 1
        elif result == 0:
            skip_count += 1
        elif result == -1:
            fail_count += 1

    print("\nConversion complete:")
    print(f"  Successful: {success_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Failed: {fail_count}")
    
    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='Convert font files between TTF, WOFF, and WOFF2 formats'
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-f', '--file',
        help='Input font file to convert'
    )
    input_group.add_argument(
        '-d', '--directory',
        help='Input directory containing font files to convert (recursive)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (for -f) or output directory (for -d)'
    )
    
    parser.add_argument(
        '-t', '--target',
        required=True,
        choices=['ttf', 'woff', 'woff2'],
        help='Target font format'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite existing output files/directories'
    )
    
    args = parser.parse_args()
    if args.file:
        success = process_single_file(args)
    else:
        success = process_directory(args)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

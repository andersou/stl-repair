# STL Repair

A command-line tool for repairing STL files using Blender's mesh repair capabilities.

## Features

- Repair common STL mesh issues (non-manifold geometry, holes, etc.)
- Automatic installation and use of Blender's 3D Print add-on
- Fallback to basic mesh repair operations
- Command-line interface for easy integration into workflows
- Supports batch processing

## Requirements

- Python 3.11 or higher
- Blender Python API (bpy)

**Important**: This tool must be run within Blender's Python environment, not standalone Python.

## Installation

### Option 1: Install from source

```bash
# Clone the repository
git clone https://github.com/andersou/stl-repair.git
cd stl-repair

# Install the package
pip install -e .
```

### Option 2: Use without installation (using uv)

```bash
# Clone the repository
git clone https://github.com/andersou/stl-repair.git
cd stl-repair

# Run directly with uv (no installation required)
uv run stl-repair input.stl [OPTIONS]
```

## Usage

### Command Line Options

```bash
stl-repair input.stl [OPTIONS]

Arguments:
  input                 Input STL file path

Options:
  -o, --output PATH     Output STL file path (default: input file with _fixed suffix)
  -s, --suffix TEXT     Suffix for output file if --output not specified (default: _fixed)
  -v, --verbose INT     Verbosity level 0-3 (default: 2)
  --no-log-file         Do not write a log file
  --force-basic         Skip 3D Print add-on and use basic repair only
  -h, --help           Show this message and exit
```

### Examples

```bash
# Basic repair (installed)
stl-repair model.stl

# Basic repair (using uv without installation)
uv run stl-repair model.stl

# Specify output file
stl-repair model.stl -o repaired_model.stl
# or with uv:
uv run stl-repair model.stl -o repaired_model.stl

# Use custom suffix
stl-repair model.stl -s "_cleaned"
# or with uv:
uv run stl-repair model.stl -s "_cleaned"

# Force basic repair (skip 3D Print add-on)
stl-repair model.stl --force-basic
# or with uv:
uv run stl-repair model.stl --force-basic

# Verbose output
stl-repair model.stl -v 3
# or with uv:
uv run stl-repair model.stl -v 3
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/andersou/stl-repair.git
cd stl-repair

# Run with uv (automatically manages dependencies)
uv run stl-repair
```

## How It Works

1. **Import**: Loads the STL file into Blender
2. **Repair**: Applies mesh repair operations:
   - Removes duplicate vertices
   - Fills holes in the mesh
   - Makes normals consistent
   - Uses Blender's 3D Print add-on for advanced repairs (if available)
3. **Export**: Saves the repaired mesh as a new STL file

## Limitations

- Requires Blender's Python environment
- May not fix all types of mesh issues
- Large files may require significant memory and processing time

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
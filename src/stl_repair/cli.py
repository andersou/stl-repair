#!/usr/bin/env python3
"""CLI entry point for STL repair tool."""
from __future__ import annotations
import argparse
import importlib
import os
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from loguru import logger

# Try to import bpy early with clear error
try:
    import bpy  # type: ignore
except Exception as e:
    logger.error(
        f"ERROR: This script must be executed inside Blender's Python. ({e})",
        file=sys.stderr,
    )
    sys.exit(1)


def attempt_install_print_addon() -> bool:
    """Attempt to install the Blender 3D print add-on."""
    try:
        user_addon_dir = bpy.utils.user_resource("SCRIPTS", path="addons", create=True)
        addon_folder = os.path.join(user_addon_dir, "object_print3d_utils")
        if not os.path.isdir(addon_folder):
            logger.info("Downloading object_print3d_utils (blender-addons main)...")
            url = (
                "https://github.com/blender/blender-addons/archive/refs/heads/main.zip"
            )
            with tempfile.TemporaryDirectory() as td:
                zip_path = os.path.join(td, "addons.zip")
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path) as zf:
                    for m in zf.namelist():
                        if m.startswith("blender-addons-main/object_print3d_utils/"):
                            rel = m.split("blender-addons-main/")[-1]
                            target_path = os.path.join(user_addon_dir, rel)
                            if m.endswith("/"):
                                os.makedirs(target_path, exist_ok=True)
                            else:
                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                with zf.open(m) as src, open(target_path, "wb") as dst:
                                    dst.write(src.read())
            logger.info("Add-on extracted to {}", addon_folder)
        importlib.invalidate_caches()
        bpy.ops.preferences.addon_enable(module="object_print3d_utils")
        logger.info("Enabled object_print3d_utils after install")
        return True
    except Exception as e:
        logger.warning(f"Automatic add-on install failed: {e}")
        return False


def enable_print_addon() -> bool:
    """Enable the Blender 3D print add-on."""
    try:
        import addon_utils  # type: ignore

        res = addon_utils.check("object_print3d_utils")
        # Blender versions differ: sometimes (enabled, loaded)
        if any(res):
            try:
                bpy.ops.preferences.addon_enable(module="object_print3d_utils")
                logger.debug("3D Print add-on enabled")
                return True
            except Exception as e:
                logger.debug(f"Enable failure: {e}")
        logger.info("3D Print add-on not present; attempting install")
        return attempt_install_print_addon()
    except Exception as e:
        logger.debug(f"Add-on check failed: {e}")
        return False


def safe_call(op_path: str, **kwargs) -> bool:
    """Call a Blender operator if it exists."""
    mod, name = op_path.rsplit(".", 1)
    ops_mod = getattr(bpy.ops, mod, None)
    if ops_mod is None or not hasattr(ops_mod, name):
        logger.debug(f"Operator missing: bpy.ops.{op_path}")
        return False
    try:
        getattr(ops_mod, name)(**kwargs)
        return True
    except Exception as e:
        logger.debug(f"Operator {op_path} failed: {e}")
        return False


def basic_mesh_repair(obj):
    """Apply basic mesh repair operations."""
    logger.info("Applying basic mesh repair")
    bpy.context.view_layer.objects.active = obj
    safe_call("object.mode_set", mode="EDIT")
    safe_call("mesh.select_all", action="SELECT")
    # Merge by distance (replace old remove_doubles)
    if not safe_call("mesh.remove_doubles"):  # older
        safe_call("mesh.merge_by_distance")
    safe_call("mesh.fill_holes")
    safe_call("mesh.normals_make_consistent", inside=False)
    safe_call("object.mode_set", mode="OBJECT")


def repair_stl(input_path: Path, output_path: Path, use_print_addon: bool, suffix: str):
    """Repair an STL file using Blender."""
    # Reset scene
    safe_call("object.select_all", action="SELECT")
    safe_call("object.delete", use_global=False, confirm=False)

    # Import
    if not safe_call(
        "wm.stl_import", filepath=str(input_path), directory=str(input_path.parent)
    ):
        raise RuntimeError("Failed to import STL")

    obj = bpy.context.view_layer.objects.active or bpy.context.selected_objects[0]
    safe_call("object.origin_set", type="ORIGIN_CENTER_OF_VOLUME", center="MEDIAN")
    for i in range(3):
        obj.location[i] = 0.0

    if suffix:
        obj.name = obj.name + suffix

    if use_print_addon:
        try:
            logger.info("Running 3D Print add-on checks")
            safe_call("mesh.print3d_check_all")
            safe_call("mesh.print3d_clean_non_manifold")
        except Exception as e:
            logger.warning(f"3D print utilities failed: {e}")
            basic_mesh_repair(obj)
    else:
        basic_mesh_repair(obj)

    # Export (export_selected_objects with batch expects directory path)
    export_dir = output_path.parent
    export_name = output_path.stem
    old_name = obj.name
    obj.name = export_name  # ensure expected filename
    if not safe_call(
        "wm.stl_export",
        filepath=str(export_dir) + os.sep,
        display_type="DEFAULT",
        use_batch=True,
        export_selected_objects=True,
    ):
        raise RuntimeError("Failed to export STL")
    final_file = export_dir / f"{obj.name}.stl"
    obj.name = old_name  # restore
    logger.info(f"Wrote {final_file}")
    return final_file


def parse_args():
    """Parse command line arguments."""
    p = argparse.ArgumentParser(description="Repair a single STL file using Blender.")
    p.add_argument("input", type=Path, help="Input STL file")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output STL file path (default: alongside input with suffix)",
    )
    p.add_argument(
        "-s",
        "--suffix",
        default="_fixed",
        help="Suffix if output not provided (default: _fixed)",
    )
    p.add_argument(
        "-v", "--verbose", type=int, default=2, help="Verbosity 0-3 (default: 2)"
    )
    p.add_argument("--no-log-file", action="store_true", help="Do not write a log file")
    p.add_argument(
        "--force-basic",
        action="store_true",
        help="Skip attempting to use/ install 3D print add-on",
    )
    return p.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_args()
    if not args.input.exists():
        logger.error("Input file does not exist: {}", args.input)
        sys.exit(1)

    output = args.output
    if output is None:
        output = args.input.with_stem(args.input.stem + args.suffix)
    if output.suffix.lower() != ".stl":
        output = output.with_suffix(".stl")

    logger.info(f"Repairing {args.input}")
    use_addon = False
    if not args.force_basic:
        use_addon = enable_print_addon()
        if not use_addon:
            logger.info("Proceeding without 3D Print add-on")

    try:
        final_file = repair_stl(
            args.input, output, use_addon, "" if args.output else args.suffix
        )
        logger.info(f"Repaired file saved: {final_file}")
    except Exception as e:
        logger.exception(f"Repair failed: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()

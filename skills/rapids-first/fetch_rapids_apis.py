"""Fetch the public APIs of RAPIDS-related packages in the current Python environment.

For each package, traverse all its submodules and extract the "fully qualified name +
signature + first line of docstring" for public functions, classes, and class methods,
one API per line, written to ``<output_dir>/apis/<package>.txt``.

Design goals:
- Each line is self-contained, convenient for ``ripgrep`` search → a single match
  yields both the call syntax and purpose;
- The same qualname is kept only once, but all re-export paths are allowed to appear
  (e.g., ``cuml.KMeans`` and ``cuml.cluster.KMeans`` both exist, corresponding to the
  submodule paths in cpu-rapids-cuda-mapping.tsv);
- Skip private names (``_*``), purely internal subtrees (e.g., ``cudf.core``), and
  objects not defined in this package;
- A single package's failure does not affect other packages (submodule import
  exceptions are silently skipped).

Usage::

    python fetch_rapids_apis.py                # Fetch the default 4 RAPIDS packages
    python fetch_rapids_apis.py --packages cudf cuml
    python fetch_rapids_apis.py --output-dir /tmp/rapids-apis
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import pkgutil
import sys
import warnings
from pathlib import Path
from typing import Iterable

# RAPIDS core stack, roughly ordered by usage frequency
DEFAULT_PACKAGES = [
    "cupy",
    "cupyx",
    "cudf",
    "cuml",
]

# Skip purely internal implementation subtrees: objects under these paths are usually
# already exposed via higher-level re-exports, and re-listing them only bloats
# apis/<pkg>.txt and produces noise (e.g., cudf.core.dataframe.DataFrame is already
# retrievable via cudf.DataFrame).
# Key is the top-level package name; value is a tuple of prefixes (full module path
# prefix, either ending with . or matching exactly).
DEFAULT_SKIP_SUBTREES: dict[str, tuple[str, ...]] = {
    "cudf": ("cudf.core",),
    # cuml.benchmark is a standalone benchmarking harness (runners, dataset loaders,
    # timing helpers), not part of the estimator API users target when writing code.
    "cuml": (
        "cuml.internals",
        "cuml.thirdparty_adapters",
        "cuml.common",
        "cuml.prims",
        "cuml.benchmark",
    ),
}


def _is_skipped(modname: str, skip_subtrees: tuple[str, ...]) -> bool:
    """Determine whether modname falls under any of the skip subtrees."""
    for prefix in skip_subtrees:
        if modname == prefix or modname.startswith(prefix + "."):
            return True
    return False


def _is_public(name: str) -> bool:
    """A name not starting with ``_`` is considered public."""
    return not name.startswith("_")


def _first_doc_line(obj: object) -> str:
    """Extract the first non-empty line of the docstring; return an empty string on failure."""
    try:
        doc = inspect.getdoc(obj)
    except Exception:
        return ""
    if not doc:
        return ""
    for line in doc.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _signature_str(obj: object) -> str:
    """Return the signature string; fall back to ``(...)`` for C extensions or when introspection fails."""
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return "(...)"


def _iter_submodules(pkg, pkg_name: str, skip_subtrees: tuple[str, ...]) -> Iterable:
    """Recursively traverse submodules within a package, automatically skipping private
    paths, modules that fail to import, and purely internal subtrees in ``skip_subtrees``."""
    yield pkg
    if not hasattr(pkg, "__path__"):
        return
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            # onerror intercepts all submodule import errors (including non-ImportError
            # like RuntimeError); otherwise walk_packages would let the exception
            # bubble up and terminate the entire fetching process
            walker = pkgutil.walk_packages(
                pkg.__path__,
                prefix=pkg_name + ".",
                onerror=lambda _name: None,
            )
        except Exception:
            return
        while True:
            try:
                _finder, modname, _ispkg = next(walker)
            except StopIteration:
                return
            except Exception:
                # Exception inside the walker before yielding (rare); skip entirely to avoid hanging
                continue
            # Skip any path whose segment starts with _ (private submodules)
            if any(seg.startswith("_") for seg in modname.split(".")):
                continue
            # Skip internal directories like tests / benchmarks; note ``testing`` is not in
            # the list because cupy.testing / cudf.testing / cuml.testing are public APIs
            # (for users to write unit tests). ``_testing`` is already filtered out by the ``_`` prefix.
            if any(seg in {"tests", "benchmarks", "examples"}
                   for seg in modname.split(".")):
                continue
            # Skip purely internal implementation subtrees
            if _is_skipped(modname, skip_subtrees):
                continue
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    yield importlib.import_module(modname)
            except Exception:
                continue


def _belongs_to(obj: object, pkg_name: str) -> bool:
    """Whether the object belongs to the target package (based on ``__module__``)."""
    mod = getattr(obj, "__module__", None)
    if mod is None:
        return False
    return mod == pkg_name or mod.startswith(pkg_name + ".")


def _collect_class_members(cls, qualname: str, emit) -> None:
    """Collect public methods of a class, prioritizing the class's own methods in
    ``__dict__``; inherited methods are also kept (users commonly use them too)."""
    try:
        members = inspect.getmembers(cls)
    except Exception:
        return
    for name, obj in members:
        if not _is_public(name):
            continue
        # Only collect callable objects (methods / functions / property / classmethod, etc.)
        if not (callable(obj) or isinstance(obj, (property, staticmethod, classmethod))):
            continue
        emit(f"{qualname}.{name}", obj)


def fetch_package(pkg_name: str, output_dir: Path,
                  skip_subtrees: tuple[str, ...] = ()) -> int:
    """Fetch a single package and write to ``<output_dir>/apis/<pkg_name>.txt``. Returns the number of entries."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pkg = importlib.import_module(pkg_name)
    except Exception as exc:
        print(f"[skip] {pkg_name}: import failed -> {exc}", file=sys.stderr)
        return 0

    # Deduplicate by qualname (when the same qualname is captured multiple times,
    # keep the first occurrence), but allow the same object to appear under different
    # qualnames — this way, re-export entry points (e.g., ``cuml.KMeans`` and
    # ``cuml.cluster.KMeans``) are all recorded, consistent with the submodule paths
    # in cpu-rapids-cuda-mapping.tsv.
    entries: dict[str, tuple[str, str]] = {}  # qualname -> (sig, doc)

    def emit(qualname: str, obj: object) -> None:
        if qualname in entries:
            return
        sig = _signature_str(obj) if callable(obj) else ""
        doc = _first_doc_line(obj)
        entries[qualname] = (sig, doc)

    for module in _iter_submodules(pkg, pkg_name, skip_subtrees):
        try:
            mod_name = module.__name__
        except Exception:
            continue

        # Prefer __all__; otherwise dir()
        public_names = list(getattr(module, "__all__", None) or [])
        if not public_names:
            try:
                public_names = [n for n in dir(module) if _is_public(n)]
            except Exception:
                continue

        for name in public_names:
            if not _is_public(name):
                continue
            try:
                obj = getattr(module, name)
            except Exception:
                continue

            # Only collect objects belonging to this package (avoid those re-exported from numpy, etc.)
            if inspect.ismodule(obj):
                continue
            if not _belongs_to(obj, pkg_name):
                continue

            qualname = f"{mod_name}.{name}"
            emit(qualname, obj)

            if inspect.isclass(obj):
                _collect_class_members(obj, qualname, emit)

    # Output: sort lexicographically for stable diffs
    out_path = output_dir / "apis" / f"{pkg_name}.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for qualname, (sig, doc) in sorted(entries.items()):
        if doc:
            lines.append(f"{qualname}{sig} - {doc}")
        else:
            lines.append(f"{qualname}{sig}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok] {pkg_name}: {len(lines)} entries -> {out_path}")
    return len(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent),
        help="Output root directory; defaults to the script's directory. Each package is written to <output_dir>/apis/<pkg>.txt",
    )
    parser.add_argument(
        "--packages",
        nargs="*",
        default=DEFAULT_PACKAGES,
        help="Names of packages to fetch (import names, not PyPI names)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[info] output_dir = {output_dir}")
    print(f"[info] packages   = {args.packages}")

    total = 0
    for pkg_name in args.packages:
        skip = DEFAULT_SKIP_SUBTREES.get(pkg_name, ())
        total += fetch_package(pkg_name, output_dir, skip_subtrees=skip)
    print(f"[done] total entries: {total}")


if __name__ == "__main__":
    main()

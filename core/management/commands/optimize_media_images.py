import os
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


class Command(BaseCommand):
    help = "Resize and compress uploaded JPEG, PNG, and WebP images in place."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Write optimized images. Without this flag, only report candidates.",
        )
        parser.add_argument(
            "--max-width",
            type=int,
            default=1600,
            help="Maximum image width in pixels (default: 1600).",
        )
        parser.add_argument(
            "--max-height",
            type=int,
            default=1200,
            help="Maximum image height in pixels (default: 1200).",
        )
        parser.add_argument(
            "--quality",
            type=int,
            default=82,
            help="JPEG/WebP quality from 1 to 95 (default: 82).",
        )

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT).resolve()
        apply_changes = options["apply"]
        max_width = options["max_width"]
        max_height = options["max_height"]
        quality = options["quality"]

        if max_width < 1 or max_height < 1:
            raise CommandError("Maximum dimensions must be positive integers.")
        if quality < 1 or quality > 95:
            raise CommandError("Quality must be between 1 and 95.")
        if not media_root.exists():
            raise CommandError(f"Media directory does not exist: {media_root}")

        scanned = optimized = skipped = errors = 0
        original_total = optimized_total = 0

        for path in sorted(media_root.rglob("*")):
            if not path.is_file():
                continue

            scanned += 1
            try:
                result = self._process_image(
                    path,
                    apply_changes=apply_changes,
                    max_size=(max_width, max_height),
                    quality=quality,
                )
            except (OSError, UnidentifiedImageError) as exc:
                errors += 1
                self.stderr.write(f"ERROR {path.relative_to(media_root)}: {exc}")
                continue

            if result is None:
                skipped += 1
                continue

            original_size, new_size, new_dimensions = result
            optimized += 1
            original_total += original_size
            optimized_total += new_size
            action = "OPTIMIZED" if apply_changes else "WOULD OPTIMIZE"
            saving = max(original_size - new_size, 0)
            self.stdout.write(
                f"{action} {path.relative_to(media_root)} "
                f"to {new_dimensions[0]}x{new_dimensions[1]} "
                f"({self._format_bytes(original_size)} -> "
                f"{self._format_bytes(new_size)}, saved {self._format_bytes(saving)})"
            )

        total_saving = max(original_total - optimized_total, 0)
        mode = "Applied" if apply_changes else "Dry run"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: scanned {scanned}, candidates {optimized}, "
                f"skipped {skipped}, errors {errors}, "
                f"potential savings {self._format_bytes(total_saving)}."
            )
        )

    def _process_image(self, path, *, apply_changes, max_size, quality):
        original_size = path.stat().st_size

        with Image.open(path) as source:
            image_format = source.format
            if image_format not in SUPPORTED_FORMATS:
                return None

            image = ImageOps.exif_transpose(source)
            original_dimensions = image.size
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            new_dimensions = image.size

            save_options = {}
            if image_format == "JPEG":
                if image.mode not in ("RGB", "L"):
                    image = image.convert("RGB")
                save_options = {
                    "quality": quality,
                    "optimize": True,
                    "progressive": True,
                }
            elif image_format == "PNG":
                save_options = {"optimize": True, "compress_level": 9}
            elif image_format == "WEBP":
                save_options = {"quality": quality, "method": 6}

            suffix = path.suffix or f".{image_format.lower()}"
            fd, temporary_name = tempfile.mkstemp(
                prefix=f".{path.stem}-",
                suffix=suffix,
                dir=path.parent,
            )
            os.close(fd)
            temporary_path = Path(temporary_name)

            try:
                image.save(temporary_path, format=image_format, **save_options)
                new_size = temporary_path.stat().st_size

                if new_size >= original_size and new_dimensions == original_dimensions:
                    return None

                if apply_changes:
                    temporary_path.replace(path)
                return original_size, new_size, new_dimensions
            finally:
                temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _format_bytes(size):
        value = float(size)
        for unit in ("B", "KB", "MB", "GB"):
            if value < 1024 or unit == "GB":
                return f"{value:.1f} {unit}"
            value /= 1024

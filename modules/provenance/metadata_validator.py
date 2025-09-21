import exifread

def validate_metadata(image_path: str) -> dict:
    """
    Checks EXIF metadata for signs of tampering.
    """
    results = {"metadata_flags": []}

    try:
        with open(image_path, "rb") as f:
            tags = exifread.process_file(f)

        if not tags:
            results["metadata_flags"].append("No EXIF metadata found (possible tampering)")

        if "Image Software" in tags:
            results["software"] = str(tags["Image Software"])
            if "photoshop" in results["software"].lower():
                results["metadata_flags"].append("Edited with Photoshop")

        if "Image DateTime" not in tags:
            results["metadata_flags"].append("Missing timestamp metadata")
    except Exception as e:
        results["metadata_flags"].append(f"Metadata error: {str(e)}")

    return results

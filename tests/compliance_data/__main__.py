import compliance_data


def extract_to_json():
    from pathlib import Path
    import json

    json_folder = Path(__file__).parent / "json_output"

    json_folder.mkdir(exist_ok=True)

    for name in compliance_data.__all__:
        mod = getattr(compliance_data, name)

        data = {
            "output": mod.output,
            "is_error": mod.is_error,
        }

        json_data = json.dumps(data, indent=2)
        output_path = json_folder / f"{name}.json"
        output_path.write_text(json_data)
        print(f"Exported: {output_path}")


print("Exporting Compliance Test Output Data")
extract_to_json()

import os

def patch_robots_config():
    file_name = "game.yml"
    file_path = os.path.join(os.path.dirname(__file__), file_name)

    with open(file_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []

    # Track state
    inside_red_hulk = False
    inside_class1_driller = False
    inside_cloaked_driller = False
    inside_fusion_hulk = False
    indentation = "    "

    # Track what fields we have seen
    red_hulk_flags = {
        "SuppressChance": False,
        "BurstDelay": False,
        "HitPoints": False,
        "StunResist": False
    }

    class1_driller_flags = {
        "StunResist": False
    }

    cloaked_driller_flags = {
        "StunResist": False
    }

    fusion_hulk_flags = {
        "FireDelay": False
    }

    # Target values
    red_hulk_target = {
        "SuppressChance": "0.1",
        "BurstDelay": "0.5",
        "HitPoints": "270",
        "StunResist": "0.4"
    }

    class1_driller_target = {
        "StunResist": "0.3"
    }

    cloaked_driller_target = {
        "StunResist": "0.3"
    }

    fusion_hulk_target = {
        "FireDelay": "[ 3, 2, 2.5, 2, 1.5 ]"
    }

    # Mapping of objects to their state, flags, and targets
    object_mappings = [
        ("Red Hulk", lambda: inside_red_hulk, red_hulk_flags, red_hulk_target),
        ("Class 1 Driller", lambda: inside_class1_driller, class1_driller_flags, class1_driller_target),
        ("Cloaked Driller", lambda: inside_cloaked_driller, cloaked_driller_flags, cloaked_driller_target),
        ("Fusion hulk", lambda: inside_fusion_hulk, fusion_hulk_flags, fusion_hulk_target)
    ]

    def write_missing_fields(flags, target_dict):
        """Append missing fields to the current section."""
        result = []
        for key, found in flags.items():
            if not found:
                value = target_dict[key]
                result.append(f"{indentation}{key}: {value}\n")
        return result

    def flush_object_end(missing_fields):
        """Flushes any missing fields to the current object."""
        if updated_lines and updated_lines[-1].strip() == "":
            last_blank = updated_lines.pop()
            updated_lines.extend(missing_fields)
            updated_lines.append(last_blank)
        else:
            updated_lines.extend(missing_fields)

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Start of a new object
        if stripped.startswith("- id:"):
            for _, inside_fn, flags, target in object_mappings:
                if inside_fn():
                    flush_object_end(write_missing_fields(flags, target))
                    for k in flags:
                        flags[k] = False  # Reset flags

            inside_red_hulk = inside_class1_driller = inside_cloaked_driller = inside_fusion_hulk = False

        # Detect object names and set state
        if stripped.startswith("Name: Red Hulk"):
            inside_red_hulk = True
        elif stripped.startswith("Name: Class 1 Driller"):
            inside_class1_driller = True
        elif stripped.startswith("Name: Cloaked Driller"):
            inside_cloaked_driller = True
        elif stripped.startswith("Name: Fusion hulk"):
            inside_fusion_hulk = True

        if any(fn() for _, fn, _, _ in object_mappings):
            if stripped.startswith("#"):
                updated_lines.append(line)
                i += 1
                continue

            current_flags = None
            current_target = None
            for _, inside_fn, flags, target in object_mappings:
                if inside_fn():
                    current_flags = flags
                    current_target = target
                    break

            if current_flags is None:
                updated_lines.append(line)
                i += 1
                continue

            matched = False
            for key in current_flags:
                if stripped.startswith(f"{key}:"):
                    leading_spaces = line[:len(line) - len(line.lstrip())]
                    updated_lines.append(f"{leading_spaces}{key}: {current_target[key]}\n")
                    current_flags[key] = True
                    matched = True
                    break

            if not matched:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

        i += 1

    # Final flush in case file ends while still inside an object
    for _, inside_fn, flags, target in object_mappings:
        if inside_fn():
            flush_object_end(write_missing_fields(flags, target))

    # Write back to file
    with open(file_path, 'w') as f:
        f.writelines(updated_lines)

if __name__ == "__main__":
    patch_robots_config()



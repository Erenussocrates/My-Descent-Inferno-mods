import os
import re

def patch_weapons_config():
    file_name = "game.yml"
    file_path = os.path.join(os.path.dirname(__file__), file_name)

    with open(file_path, 'r') as f:
        lines = f.readlines()

    updated_lines = []
    i = 0

    current_block = None

    # Flags to track if we've already seen certain keys
    flags = {
        "vulcan": {"Spread": False, "StunMult": False},
        "spreadfire": {"Spread": False, "Damage": False, "EnergyUsage": False, "IsHoming": False, "HomingFov": False, "HomingDistance": False, "HomingTurnRate": False},
        "fusion": {"StunMult": False, "Damage": False},
        "concussion missile": {"StunMult": False},
        "homing missile": {"StunMult": False},
        "fusion_charge": {"Width": False},
        "Weapon: Fusion": {"Gunpoints": False}
    }

    # Target values to insert
    targets = {
        "vulcan": {"Spread": "1.8", "StunMult": "2.75"},
        "spreadfire": {"Spread": "3.6", "Damage": "11", "EnergyUsage": "0.6", "IsHoming": "true", "HomingFov": "11.25", "HomingDistance": "75", "HomingTurnRate": "75"},
        "fusion": {"StunMult": "1.1", "Damage": "120"},
        "concussion missile": {"StunMult": "2"},
        "homing missile": {"StunMult": "2"},
        "fusion_charge": {"Width": "0"},
        "Weapon: Fusion": {"Gunpoints": "6"}
    }

    # Define hardcoded indentation per block
    indent_map = {
        "fusion_charge": "      ",       # 6 spaces
        "Weapon: Fusion": "            ", # 12 spaces
    }

    def flush_missing_fields(block):
        indent = indent_map.get(block, "    ")  # Default to 4 spaces
        result = []
        for key, seen in flags[block].items():
            if not seen:
                result.append(f"{indent}{key}: {targets[block][key]}\n")
        return result

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # New block, flush current if needed
        if stripped.startswith("- id:") or re.match(r"^\s*- Name: ", line):
            if current_block in flags:
                updated_lines.extend(flush_missing_fields(current_block))
            current_block = None
            # Reset all flags
            for key in flags:
                for f in flags[key]:
                    flags[key][f] = False

        # Identify current block by name
        if stripped.startswith("Name: "):
            name_value = stripped[6:].strip()
            if name_value in flags:
                current_block = name_value

        elif stripped.startswith("- Name: fusion_charge"):
            current_block = "fusion_charge"

        elif stripped.startswith("- Weapon: Fusion"):
            current_block = "Weapon: Fusion"
            updated_lines.append(line)
            i += 1

            in_firing = False
            found_gunpoints = False
            firing_indent = indent_map["Weapon: Fusion"]

            while i < len(lines):
                sub_line = lines[i]
                sub_stripped = sub_line.strip()

                if sub_stripped.startswith("Firing:"):
                    in_firing = True
                    updated_lines.append(sub_line)
                    i += 1
                    continue

                if in_firing:
                    if re.match(r"^\s*-\s*Delay:", sub_line):
                        updated_lines.append(sub_line)
                        i += 1
                        # Next line should be Gunpoints, insert or replace
                        if i < len(lines) and "Gunpoints:" in lines[i]:
                            updated_lines.append(firing_indent + "Gunpoints: " + targets[current_block]["Gunpoints"] + "\n")
                            flags[current_block]["Gunpoints"] = True
                            i += 1  # Skip original
                        else:
                            updated_lines.append(firing_indent + "Gunpoints: " + targets[current_block]["Gunpoints"] + "\n")
                            flags[current_block]["Gunpoints"] = True
                        continue

                if re.match(r"^\s*-\s*\w", sub_line) or re.match(r"^\s*\w", sub_line):
                    break

                updated_lines.append(sub_line)
                i += 1

            continue  # skip rest of normal processing

        # Key-value line update
        if current_block in flags:
            matched = False
            for key in flags[current_block]:
                if stripped.startswith(f"{key}:"):
                    indent = indent_map.get(current_block, "    ")
                    updated_lines.append(f"{indent}{key}: {targets[current_block][key]}\n")
                    flags[current_block][key] = True
                    matched = True
                    break
            if not matched:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

        i += 1

    # Final flush if needed
    if current_block in flags:
        updated_lines.extend(flush_missing_fields(current_block))

    with open(file_path, 'w') as f:
        f.writelines(updated_lines)

if __name__ == "__main__":
    patch_weapons_config()

#!/data/data/com.termux/files/usr/bin/bash

# Directory containing txt files (change if needed)
DIR="$HOME/storage/documents/notes"

# List .txt files and map them to numbers
TXT_FILES=($(ls -1 "$DIR"/*.txt 2>/dev/null))
if [ ${#TXT_FILES[@]} -eq 0 ]; then
  echo "No .txt files found in $DIR"
  exit 1
fi

echo "Select a file to open:"
for i in "${!TXT_FILES[@]}"; do
  echo "$((i+1))) ${TXT_FILES[$i]##*/}"
done

# Read user input
read -p "Enter number: " NUM

# Validate input
if ! [ "$NUM" -ge 1 ] 2>/dev/null || [ "$NUM" -gt "${#TXT_FILES[@]}" ]; then
  echo "Invalid selection."
  exit 1
fi

# Open selected file in vim
vim "${TXT_FILES[$((NUM-1))]}"


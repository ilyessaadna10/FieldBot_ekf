#!/bin/bash
# Simple Markdown to PDF converter using Pandoc
# This version uses HTML as intermediate format (no LaTeX needed)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== FieldBot Documentation PDF Generator ===${NC}\n"

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo -e "${RED}Error: pandoc is not installed${NC}"
    echo "Install with: sudo apt install pandoc"
    exit 1
fi

# Get directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$SCRIPT_DIR/../docs"
OUTPUT_DIR="$DOCS_DIR/pdf_exports"

mkdir -p "$OUTPUT_DIR"

# Determine files to convert
if [ -n "$1" ]; then
    if [ ! -f "$1" ]; then
        echo -e "${RED}Error: File not found: $1${NC}"
        exit 1
    fi
    FILES=("$1")
    echo "Converting specific file: $1"
else
    FILES=("$DOCS_DIR"/*.md)
    echo "Converting markdown files from: $DOCS_DIR"
fi

echo "Output directory: $OUTPUT_DIR"
echo ""

count=0

# Convert files
for md_file in "${FILES[@]}"; do
    if [ ! -e "$md_file" ]; then
        echo "File not found: $md_file"
        continue
    fi
    
    filename=$(basename "$md_file" .md)
    pdf_file="$OUTPUT_DIR/${filename}.pdf"
    
    echo -e "${YELLOW}Converting: ${filename}.md${NC}"
    
    # Method 1: Direct pandoc with wkhtmltopdf (if available)
    if command -v wkhtmltopdf &> /dev/null; then
        pandoc "$md_file" -o "$pdf_file" \
            --pdf-engine=wkhtmltopdf \
            --css=<(echo "body{font-family: Arial; margin: 2cm; line-height: 1.6;}") \
            2>/dev/null && {
            echo -e "${GREEN}  ✓ Created: ${filename}.pdf${NC}"
            ((count++))
            continue
        }
    fi
    
    # Method 2: Fallback - Convert to HTML first
    html_file="$OUTPUT_DIR/${filename}.html"
    pandoc "$md_file" -o "$html_file" \
        --self-contained \
        --css=<(echo "body{max-width: 800px; margin: auto; padding: 2em; font-family: Arial;}") \
        2>/dev/null && {
        echo -e "${GREEN}  ✓ Created HTML: ${filename}.html${NC}"
        echo -e "    ${YELLOW}Note: Install wkhtmltopdf for direct PDF conversion${NC}"
        ((count++))
    }
done

echo ""
echo -e "${GREEN}=== Conversion Complete ===${NC}"
echo "Converted $count file(s)"
echo "Files saved to: $OUTPUT_DIR"

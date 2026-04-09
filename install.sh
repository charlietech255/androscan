set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[*] Installing androidscan Advanced for Termux...${NC}"

# Check kama ina run ndani ya Termux
if [[ -z "$PREFIX" ]]; then
    echo -e "${RED}[-] hii script lazima iwe ndani ya Termux.${NC}"
    exit 1
fi

# hakikisha script za py kama zipo
if [[ ! -f "androscan.py" ]]; then
    echo -e "${RED}[-] androscan.py haipo kwenye files.${NC}"
    exit 1
fi

# lets excute it
chmod +x androscan.py

# Copy to $PREFIX/bin (global command)
cp androscan.py $PREFIX/bin/androscan

echo -e "${GREEN}[+] Installation imekamilika!${NC}"
echo -e "${GREEN}[+] now unaeza run 'androscan' from anywhere offline.${NC}"
echo -e "${YELLOW}[!] kwa best results, run: termux-setup-storage${NC}"
echo -e "${YELLOW}[!] Optional: pkg install termux-api (for sensor data)${NC}"

#!/data/data/com.termux/files/usr/bin/bash
# File: ~/battery_thermal_status.sh
# Usage: ./battery_thermal_status.sh
#        or alias bt='./battery_thermal_status.sh'

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ──────────────────────────────────────────────────────────────
#  Quick ADB connection check & auto-reconnect
# ──────────────────────────────────────────────────────────────
DEVICE="127.0.0.1:5555"
MAX_TRIES=3
SLEEP_BETWEEN=2

echo -e "${CYAN}Checking ADB connection...${NC}"

if adb devices | grep -q "^${DEVICE}.*device$"; then
    echo -e "  ${GREEN}Already connected ✓${NC}"
else
    echo -e "  ${YELLOW}No connection found — trying to connect...${NC}"
    
    for i in $(seq 1 $MAX_TRIES); do
        echo -n "  Attempt $i/$MAX_TRIES... "
        adb connect $DEVICE > /dev/null 2>&1
        
        sleep $SLEEP_BETWEEN
        
        if adb devices | grep -q "^${DEVICE}.*device$"; then
            echo -e "${GREEN}Success! ✓${NC}"
            break
        else
            echo -e "${RED}Failed${NC}"
        fi
    done

    # Final check
    if ! adb devices | grep -q "^${DEVICE}.*device$"; then
        echo -e "\n${RED}Could not connect after ${MAX_TRIES} attempts.${NC}"
        echo "Please make sure:"
        echo "  • Wireless debugging is ON"
        echo "  • You previously ran 'adb tcpip 5555'"
        echo "  • Wi-Fi is active on the tablet"
        exit 1
    fi
fi

echo ""
echo -e "${CYAN}┌────────────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│           Battery & Thermal Status                 │${NC}"
echo -e "${CYAN}└────────────────────────────────────────────────────┘${NC}"
echo ""

# ──────────────────────────────────────────────────────────────
#  1. Battery Information
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}Battery Information:${NC}"

battery=$(dumpsys battery 2>/dev/null || /system/bin/dumpsys battery 2>/dev/null)

if [ -n "$battery" ]; then
    percent=$(echo "$battery" | grep -i "level:" | awk '{print $2}')
    echo -e "  Battery level:          ${GREEN}${percent}%${NC}"

    status=$(echo "$battery" | grep -i "status:" | awk '{print $2}')
    case $status in
        2)  charging="Charging" ;;
        3)  charging="Discharging" ;;
        5)  charging="Full" ;;
        *)  charging="Other ($status)" ;;
    esac
    echo -e "  Charging status:        ${GREEN}${charging}${NC}"

    health=$(echo "$battery" | grep -i "health:" | awk '{print $2}')
    case $health in
        2)  health_str="Good" ;;
        3)  health_str="Overheat" ;;
        7)  health_str="Cold" ;;
        *)  health_str="Other ($health)" ;;
    esac
    echo -e "  Battery health:         ${GREEN}${health_str}${NC}"

    temp_raw=$(echo "$battery" | grep -i "temperature:" | awk '{print $2}')
    if [ -n "$temp_raw" ]; then
        temp_c=$(awk "BEGIN {print $temp_raw / 10}")
        echo -e "  Battery temperature:    ${GREEN}${temp_c} °C${NC}"
    fi

    current=$(echo "$battery" | grep -i "current now:" | awk '{print $3}')
    if [ -n "$current" ]; then
        current_ma=$(awk "BEGIN {print $current / 1000}")
        sign=$([ "$current" -lt 0 ] && echo "charging" || echo "discharging")
        echo -e "  Current:                ${GREEN}${current_ma} mA (${sign})${NC}"
    fi
else
    echo -e "  ${RED}Battery info not available${NC}"
fi

echo ""

# ──────────────────────────────────────────────────────────────
#  2. Thermal Information (CPU / GPU / SoC)
# ──────────────────────────────────────────────────────────────
echo -e "${YELLOW}Thermal Information:${NC}"

thermal=$(/system/bin/dumpsys thermalservice 2>/dev/null)

if [ -n "$thermal" ]; then
    cpu_temp=$(echo "$thermal" | grep -i -E 'Temperature.*(cpu|soc|ap|tsens|cluster)' | grep -oP 'mValue=\K[\d.]+' | head -1)
    gpu_temp=$(echo "$thermal" | grep -i -E 'Temperature.*(gpu|mali|adreno)' | grep -oP 'mValue=\K[\d.]+' | head -1)

    [ -n "$cpu_temp" ] && echo -e "  CPU / SoC:              ${GREEN}${cpu_temp} °C${NC}" || echo -e "  CPU / SoC:              ${YELLOW}not detected${NC}"
    [ -n "$gpu_temp" ] && echo -e "  GPU:                    ${GREEN}${gpu_temp} °C${NC}" || echo -e "  GPU:                    ${YELLOW}not detected${NC}"

    echo ""
    echo -e "${CYAN}First few temperature readings:${NC}"
    echo "$thermal" | grep -i Temperature | head -n 5
else
    echo -e "  ${RED}thermalservice not responding${NC}"
fi

echo ""
echo -e "${CYAN}──────────────────────────────────────────────────────${NC}"

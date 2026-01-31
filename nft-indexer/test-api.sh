#!/bin/bash

# API Testing Script
# Тестирование всех endpoints NFT Indexer API

set -e

API_BASE="${1:-http://localhost:3001}"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  NFT Indexer API Testing Suite      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "API Base URL: ${YELLOW}$API_BASE${NC}"
echo ""

# Test function
test_endpoint() {
    local name=$1
    local endpoint=$2
    local expected_status=${3:-200}

    echo -ne "Testing ${BLUE}$name${NC}... "

    response=$(curl -s -w "\n%{http_code}" "$API_BASE$endpoint")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} ($http_code)"
        # Pretty print JSON if jq is available
        if command -v jq &> /dev/null; then
            echo "$body" | jq -C '.' 2>/dev/null | head -n 20 || echo "$body" | head -c 200
        else
            echo "$body" | head -c 200
        fi
        echo ""
    else
        echo -e "${RED}✗${NC} ($http_code, expected $expected_status)"
        echo "$body"
        echo ""
    fi
}

# Run tests
echo -e "${YELLOW}[1/10]${NC} Health Check"
test_endpoint "GET /health" "/health"

echo -e "${YELLOW}[2/10]${NC} Collections"
test_endpoint "GET /api/collections" "/api/collections"

echo -e "${YELLOW}[3/10]${NC} NFTs (all)"
test_endpoint "GET /api/nfts?limit=5" "/api/nfts?limit=5"

echo -e "${YELLOW}[4/10]${NC} NFTs (on sale)"
test_endpoint "GET /api/nfts?on_sale=true&limit=5" "/api/nfts?on_sale=true&limit=5"

echo -e "${YELLOW}[5/10]${NC} Listings"
test_endpoint "GET /api/listings?limit=5" "/api/listings?limit=5"

echo -e "${YELLOW}[6/10]${NC} Markets"
test_endpoint "GET /api/markets" "/api/markets"

echo -e "${YELLOW}[7/10]${NC} Trending NFTs"
test_endpoint "GET /api/trending?limit=5" "/api/trending?limit=5"

echo -e "${YELLOW}[8/10]${NC} Price Drops"
test_endpoint "GET /api/price-drops?threshold=10" "/api/price-drops?threshold=10"

echo -e "${YELLOW}[9/10]${NC} Search"
test_endpoint "GET /api/search?q=gift" "/api/search?q=gift"

echo -e "${YELLOW}[10/10]${NC} CORS Check"
curl -s -I -H "Origin: http://localhost:3000" "$API_BASE/api/markets" | grep -i "access-control" && echo -e "${GREEN}✓${NC} CORS enabled" || echo -e "${RED}✗${NC} CORS not configured"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  API Testing Complete!               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo -e "  1. Run indexer: ${BLUE}npm run job:index-collections${NC}"
echo -e "  2. Check frontend: ${BLUE}cd ../frontend && npm run dev${NC}"
echo ""

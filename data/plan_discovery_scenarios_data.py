"""
Plan Discovery & Account Queries Scenarios Data Catalog
Contains 33 functional query test scenarios across:
- Plan Discovery by Country & Region (Japan, Vietnam, Asia Pacific, North America, Middle East, Africa, Latin America, Europe, Thailand)
- Plan Filtering by Capacity & Duration (Unlimited, 1GB to 5GB, 5GB, 10 Day Unlimited, 10GB validity & cost)
- Account Balance & Expiry (Vietnam data balance, Total balance, Expiry date)
- Referral Statistics & Sharing (Referral count, Bonuses received, Sharing referral link)
- Rewards & Data Transfer (Reward data, Transfers history, Step-by-step transfer)
- Cashback Breakdown (Current balance, Earned, Pending, Used, How to earn)
- Onboarding & Free Data (eSIM installation, How to get free data)
"""

from typing import Dict, List, Any


PLAN_DISCOVERY_SCENARIOS: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. PLAN DISCOVERY BY REGION & COUNTRY (8 Scenarios)
    # =========================================================================
    {
        "id": "DISC_01",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks to see all available data plans for Japan.",
        "expected_behavior": "List available Japan data plans (e.g. 1GB, 3GB, 5GB, 10GB, Unlimited) with prices and validity.",
        "prompt": "Show me all data plan for Japan",
        "expected_keywords": ["japan", "plan", "gb", "$", "price", "unlimited", "data"],
        "negative_keywords": []
    },
    {
        "id": "DISC_02",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks to see all available data plans for Vietnam.",
        "expected_behavior": "List available Vietnam data plans with pricing and validity details.",
        "prompt": "Show me all data plans for Vietnam",
        "expected_keywords": ["vietnam", "viet nam", "plan", "gb", "$", "price", "unlimited", "data"],
        "negative_keywords": []
    },
    {
        "id": "DISC_03",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for all regional data plans covering Asia Pacific.",
        "expected_behavior": "Present Asia Pacific regional plan options with covered countries and prices.",
        "prompt": "Show me all data plans for Asia Pacific?",
        "expected_keywords": ["asia", "pacific", "plan", "gb", "$", "regional", "countries", "data"],
        "negative_keywords": []
    },
    {
        "id": "DISC_04",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for all regional data plans for North America.",
        "expected_behavior": "List North America regional plans covering US, Canada, Mexico with prices.",
        "prompt": "Show me all data plans for North America?",
        "expected_keywords": ["north america", "america", "usa", "canada", "plan", "gb", "$", "regional"],
        "negative_keywords": []
    },
    {
        "id": "DISC_05",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for all data plans covering the Middle East region.",
        "expected_behavior": "Present Middle East regional data plan options with pricing and allowances.",
        "prompt": "Show me all data plans for Middle East?",
        "expected_keywords": ["middle east", "plan", "gb", "$", "regional", "countries", "data"],
        "negative_keywords": []
    },
    {
        "id": "DISC_06",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for data plan options for Africa.",
        "expected_behavior": "List Africa regional or country-specific plans available on Eskimo.",
        "prompt": "Show me all data plans for Africa?",
        "expected_keywords": ["africa", "plan", "gb", "$", "regional", "countries", "data"],
        "negative_keywords": []
    },
    {
        "id": "DISC_07",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for data plans covering Latin America.",
        "expected_behavior": "Present Latin America regional eSIM plan options with price details.",
        "prompt": "Show me all data plans for Latin America?",
        "expected_keywords": ["latin america", "america", "plan", "gb", "$", "regional", "countries"],
        "negative_keywords": []
    },
    {
        "id": "DISC_08",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer wants to compare different European data plans.",
        "expected_behavior": "Compare fixed vs unlimited options, pricing, and coverage across European countries.",
        "prompt": "Compare data plans for Europe",
        "expected_keywords": ["europe", "european", "plan", "gb", "fixed", "unlimited", "compare", "$"],
        "negative_keywords": []
    },

    # =========================================================================
    # 2. PLAN FILTERING & PRICING SPECIFICS (7 Scenarios)
    # =========================================================================
    {
        "id": "DISC_09",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer specifically asks for Unlimited plans for Vietnam.",
        "expected_behavior": "Display Unlimited Vietnam plan duration options (e.g. 10 days, 15 days, 30 days) and explain high-speed policy.",
        "prompt": "Show me Unlimited Viet Nam Plans",
        "expected_keywords": ["unlimited", "vietnam", "viet nam", "day", "speed", "plan", "$", "price"],
        "negative_keywords": []
    },
    {
        "id": "DISC_10",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer filters Vietnam plans within 1GB to 5GB range.",
        "expected_behavior": "Filter and list Vietnam plans within 1GB, 3GB, and 5GB with respective prices.",
        "prompt": "Show me plans from 1GB to 5GB for Viet Nam",
        "expected_keywords": ["vietnam", "viet nam", "1gb", "3gb", "5gb", "gb", "$", "plan"],
        "negative_keywords": []
    },
    {
        "id": "DISC_11",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer specifically requests a 5GB plan for Vietnam.",
        "expected_behavior": "Recommend the 5GB Vietnam plan, show price, validity (no expiry), and how to purchase.",
        "prompt": "I need a 5GB plan for VietNam",
        "expected_keywords": ["5gb", "vietnam", "viet nam", "$", "price", "plan", "no expiry"],
        "negative_keywords": []
    },
    {
        "id": "DISC_12",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks about data allowances of the Unlimited Vietnam 10 Day plan.",
        "expected_behavior": "Explain high-speed data allowance per day (e.g. 3GB/day) and reduced speed conditions for 10 days.",
        "prompt": "How much data does the Unlimited Vietnam 10 Day plan include?",
        "expected_keywords": ["unlimited", "10 day", "10 days", "vietnam", "gb", "day", "speed", "high-speed"],
        "negative_keywords": []
    },
    {
        "id": "DISC_13",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks about the validity period of the 10GB Vietnam plan.",
        "expected_behavior": "Clarify that Eskimo fixed data plans (including 10GB Vietnam) have no expiry / valid until consumed.",
        "prompt": "What is the validity of the 10GB Vietnam plan?",
        "expected_keywords": ["validity", "no expiry", "expire", "10gb", "vietnam", "keep", "consumed"],
        "negative_keywords": []
    },
    {
        "id": "DISC_14",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for the exact price of the 10GB Global plan.",
        "expected_behavior": "State the current price of the 10GB Global plan and highlight no-expiry validity across 80+ countries.",
        "prompt": "How much is the 10GB Global plan?",
        "expected_keywords": ["10gb", "global", "$", "price", "cost", "countries", "no expiry"],
        "negative_keywords": []
    },
    {
        "id": "DISC_15",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks about Thailand plan pricing.",
        "expected_behavior": "Present price tiers for Thailand plans (e.g. 1GB, 3GB, 5GB, 10GB, Unlimited).",
        "prompt": "How much does the Thailand data plan cost?",
        "expected_keywords": ["thailand", "$", "price", "cost", "plan", "gb", "1gb"],
        "negative_keywords": []
    },

    # =========================================================================
    # 3. ACCOUNT BALANCE & EXPIRY (3 Scenarios)
    # =========================================================================
    {
        "id": "DISC_16",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer inquires about remaining data on their specific Vietnam plan.",
        "expected_behavior": "Check the logged-in user's Vietnam plan balance and report remaining MB/GB or status.",
        "prompt": "How much data do I have remaining for my Vietnam plan?",
        "expected_keywords": ["vietnam", "data", "remaining", "balance", "mb", "gb", "plan", "left"],
        "negative_keywords": []
    },
    {
        "id": "DISC_17",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for general total data balance across all active plans.",
        "expected_behavior": "Retrieve and display current total data balance and list active plans.",
        "prompt": "What's my current data balance?",
        "expected_keywords": ["balance", "data", "gb", "mb", "active", "plan", "remaining", "total"],
        "negative_keywords": []
    },
    {
        "id": "DISC_18",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks when their current active plan expires.",
        "expected_behavior": "Explain validity date if unlimited, or confirm no expiry rule for fixed plans.",
        "prompt": "When does my current plan expire?",
        "expected_keywords": ["expire", "expiry", "validity", "date", "no expiry", "plan", "current"],
        "negative_keywords": []
    },

    # =========================================================================
    # 4. REFERRAL PROGRAM STATISTICS & SHARING (4 Scenarios)
    # =========================================================================
    {
        "id": "DISC_19",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks how many friends have used their referral link/code.",
        "expected_behavior": "Check account referral statistics and report the count of successful referrals.",
        "prompt": "How many people have I referred?",
        "expected_keywords": ["refer", "referred", "friend", "people", "count", "number", "0"],
        "negative_keywords": []
    },
    {
        "id": "DISC_20",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks about total referral bonus earned from inviting friends.",
        "expected_behavior": "Report total free data bonus earned (e.g. 500MB per referral) from the referral program.",
        "prompt": "What referral bonus have I received?",
        "expected_keywords": ["bonus", "referral", "data", "mb", "gb", "earned", "reward", "friend"],
        "negative_keywords": []
    },
    {
        "id": "DISC_21",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for referral data received from friends.",
        "expected_behavior": "Provide the amount of bonus referral data credited to the account.",
        "prompt": "How much referral data have I received from friends?",
        "expected_keywords": ["referral", "bonus", "data", "mb", "gb", "friend", "received", "0"],
        "negative_keywords": []
    },
    {
        "id": "DISC_22",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks where and how to find and share their referral link/code.",
        "expected_behavior": "Guide the user to Rewards tab, locate referral code/link, and explain sharing options.",
        "prompt": "How do i share my referral link ?",
        "expected_keywords": ["rewards", "referral", "link", "code", "share", "tab", "copy", "friend"],
        "negative_keywords": []
    },

    # =========================================================================
    # 5. REWARDS & DATA TRANSFERS (4 Scenarios)
    # =========================================================================
    {
        "id": "DISC_23",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for an overview of all rewards received.",
        "expected_behavior": "Summarize referral bonuses, promotional data credits, or cashback rewards in the account.",
        "prompt": "What rewards have I received?",
        "expected_keywords": ["reward", "rewards", "received", "bonus", "cashback", "data", "account"],
        "negative_keywords": []
    },
    {
        "id": "DISC_24",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer inquires about total bonus/reward data balance.",
        "expected_behavior": "State the current reward data balance available in the user's data wallet.",
        "prompt": "How much reward data do I have?",
        "expected_keywords": ["reward", "data", "balance", "mb", "gb", "bonus", "wallet", "0"],
        "negative_keywords": []
    },
    {
        "id": "DISC_25",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for transfer history / how much data sent to friends.",
        "expected_behavior": "Check transfer history and report data transferred out to other Eskimo users.",
        "prompt": "How much data have I transferred to others?",
        "expected_keywords": ["transfer", "transferred", "history", "sent", "gb", "mb", "data", "friend"],
        "negative_keywords": []
    },
    {
        "id": "DISC_26",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks step-by-step how to transfer data to another user.",
        "expected_behavior": "Guide step-by-step: open Data tab, tap Transfer, enter recipient's mobile number, choose amount, and confirm.",
        "prompt": "How do I transfer data to a friend?",
        "expected_keywords": ["transfer", "data", "friend", "mobile number", "phone", "tab", "select", "send"],
        "negative_keywords": []
    },

    # =========================================================================
    # 6. CASHBACK DETAILED QUERIES (5 Scenarios)
    # =========================================================================
    {
        "id": "DISC_27",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer inquires about current cashback balance in dollars.",
        "expected_behavior": "Report the current confirmed cashback balance amount in USD.",
        "prompt": "What's my current cashback balance?",
        "expected_keywords": ["cashback", "balance", "$", "usd", "amount", "current", "0"],
        "negative_keywords": []
    },
    {
        "id": "DISC_28",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for total cashback earned from travel bookings.",
        "expected_behavior": "Report total cumulative cashback earned from partner bookings.",
        "prompt": "How much cashback have I earned?",
        "expected_keywords": ["cashback", "earned", "total", "$", "usd", "amount", "0", "rewards"],
        "negative_keywords": []
    },
    {
        "id": "DISC_29",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks about pending cashback awaiting partner validation.",
        "expected_behavior": "Check pending status and explain verification window after travel completion.",
        "prompt": "How much cashback is pending?",
        "expected_keywords": ["pending", "cashback", "$", "usd", "status", "verification", "0"],
        "negative_keywords": []
    },
    {
        "id": "DISC_30",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks how much cashback has already been redeemed or withdrawn.",
        "expected_behavior": "Report cashback redeemed for data plans or withdrawn to bank.",
        "prompt": "How much cashback have I used?",
        "expected_keywords": ["used", "redeemed", "withdrawn", "cashback", "$", "usd", "amount", "0"],
        "negative_keywords": []
    },
    {
        "id": "DISC_31",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks how the Eskimo cashback feature works.",
        "expected_behavior": "Explain that users click through Eskimo to partners like Booking.com, Agoda, Klook to earn cashback on trips.",
        "prompt": "How do I earn cashback?",
        "expected_keywords": ["cashback", "earn", "partner", "book", "klook", "agoda", "booking", "trip"],
        "negative_keywords": []
    },

    # =========================================================================
    # 7. ONBOARDING & PROMO PERKS (2 Scenarios)
    # =========================================================================
    {
        "id": "DISC_32",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks for general eSIM installation instructions.",
        "expected_behavior": "Provide step-by-step installation instructions via Settings (QR scan or direct install) for Android and iOS.",
        "prompt": "How do I install my eSIM?",
        "expected_keywords": ["install", "esim", "settings", "qr", "add", "sim", "network", "cellular"],
        "negative_keywords": []
    },
    {
        "id": "DISC_33",
        "category": "Plan Discovery & Account Queries",
        "customer_scenario": "Customer asks how to get free data on Eskimo.",
        "expected_behavior": "Explain ways to get free data: Refer a Friend (500MB per friend), promo codes, or welcome campaigns.",
        "prompt": "I want free data",
        "expected_keywords": ["free data", "refer", "friend", "bonus", "promo", "code", "500mb", "rewards"],
        "negative_keywords": []
    }
]

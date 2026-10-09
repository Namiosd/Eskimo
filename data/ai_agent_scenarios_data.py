"""
AI Agent (Eski) Test Scenarios Data Catalog
Contains 48 structured test scenarios across 6 core business domains:
1. Sales and plan recommendations (12 scenarios)
2. Compatibility and installation (6 scenarios)
3. Connection issues during travel (7 scenarios)
4. Usage balance and plans (7 scenarios)
5. Cashback and travel bookings (9 scenarios)
6. Complaints and difficult conversations (7 scenarios)
"""

from typing import Dict, List, Any


AI_AGENT_SCENARIOS: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. SALES AND PLAN RECOMMENDATIONS (12 Scenarios)
    # =========================================================================
    {
        "id": "SALES_01",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer mainly needs maps, messaging, and restaurant searches.",
        "expected_behavior": "Ask about expected usage, recommend an appropriate plan, and explain why it fits.",
        "prompt": "I'm traveling soon and mainly need data for Google Maps, WhatsApp messaging, and searching for restaurants. What plan do you recommend?",
        "expected_keywords": ["plan", "usage", "map", "message", "gb", "fit", "recommend", "light"],
        "negative_keywords": []
    },
    {
        "id": "SALES_02",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer plans to stream video, upload content, and use a laptop hotspot.",
        "expected_behavior": "Compare fixed and unlimited plans without implying all unlimited data runs at full speed.",
        "prompt": "I plan to stream videos, upload content on social media, and use my phone as a laptop hotspot. Should I get a fixed or unlimited plan?",
        "expected_keywords": ["fixed", "unlimited", "speed", "hotspot", "high-speed", "allowance", "stream", "gb"],
        "negative_keywords": []
    },
    {
        "id": "SALES_03",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer will visit France, Italy, Germany, and Spain.",
        "expected_behavior": "Compare country, regional, and global coverage and recommend the simplest suitable option.",
        "prompt": "I will be visiting France, Italy, Germany, and Spain in one trip. What is the best and simplest plan for me?",
        "expected_keywords": ["europe", "regional", "global", "country", "france", "italy", "germany", "spain", "single", "one"],
        "negative_keywords": []
    },
    {
        "id": "SALES_04",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer is visiting Japan now and Thailand in three months.",
        "expected_behavior": "Explain coverage choices and how no expiry fixed data may support future travel.",
        "prompt": "I am traveling to Japan now and then visiting Thailand in three months. How do Eskimo plans support my travel schedule?",
        "expected_keywords": ["expiry", "no expiry", "japan", "thailand", "asia", "future", "fixed", "remaining"],
        "negative_keywords": []
    },
    {
        "id": "SALES_05",
        "category": "Sales and plan recommendations",
        "customer_scenario": "A parent needs connectivity for four family members.",
        "expected_behavior": "Check device compatibility and explain separate eSIM and data transfer options accurately.",
        "prompt": "I need connectivity for 4 family members on our family vacation. Can we share one plan or how does it work with Eskimo?",
        "expected_keywords": ["esim", "compatible", "separate", "transfer", "device", "family", "share"],
        "negative_keywords": []
    },
    {
        "id": "SALES_06",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer asks for the cheapest available plan.",
        "expected_behavior": "Ask about usage before recommending by price and explain the risk of buying too little data.",
        "prompt": "What is the cheapest plan you have? I just want the lowest price option.",
        "expected_keywords": ["usage", "price", "cheapest", "risk", "run out", "need", "1gb", "$", "lowest"],
        "negative_keywords": []
    },
    {
        "id": "SALES_07",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer needs data for video calls and hotspot use.",
        "expected_behavior": "Recommend enough capacity while setting realistic expectations for network performance.",
        "prompt": "I need data for daily Zoom video calls and hotspotting to my work laptop while traveling. What plan capacity is sufficient?",
        "expected_keywords": ["gb", "capacity", "video", "hotspot", "network", "performance", "recommend", "plan"],
        "negative_keywords": []
    },
    {
        "id": "SALES_08",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer expects the eSIM to work while the ship is at sea.",
        "expected_behavior": "Explain that service depends on supported terrestrial mobile networks.",
        "prompt": "Will my Eskimo eSIM work while our cruise ship is out at sea away from land?",
        "expected_keywords": ["sea", "cruise", "terrestrial", "land", "satellite", "port", "shore", "network", "depend"],
        "negative_keywords": []
    },
    {
        "id": "SALES_09",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer travels every month.",
        "expected_behavior": "Explain one eSIM, global coverage, no expiry fixed data, and eligible cashback.",
        "prompt": "I travel internationally almost every month for work. How does Eskimo work for frequent travelers like me?",
        "expected_keywords": ["one esim", "global", "no expiry", "cashback", "fixed", "reusable", "month", "travel"],
        "negative_keywords": []
    },
    {
        "id": "SALES_10",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer asks why they should choose Eskimo.",
        "expected_behavior": "Lead with relevant differentiators without unsupported claims or criticism of competitors.",
        "prompt": "Why should I choose Eskimo instead of other eSIM providers?",
        "expected_keywords": ["eskimo", "no expiry", "global", "transfer", "cashback", "esim", "coverage"],
        "negative_keywords": []
    },
    {
        "id": "SALES_11",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer wants to know how to redeem a gift code or voucher in the app.",
        "expected_behavior": "Guide the customer on how to redeem a gift code: navigate to Data or Data Hub, select Redeem Voucher, enter the code, and confirm.",
        "prompt": "How do I redeem a gift code?",
        "expected_keywords": ["redeem", "code", "voucher", "data", "enter", "tab", "gift"],
        "negative_keywords": []
    },
    {
        "id": "SALES_12",
        "category": "Sales and plan recommendations",
        "customer_scenario": "The customer asks if Google and WhatsApp work in China without being blocked.",
        "expected_behavior": "Confirm that Google, WhatsApp, and social media work normally in China via Eskimo eSIM roaming without requiring a VPN.",
        "prompt": "How about Google and WhatsApp? Can I receive WhatsApp msg in China?",
        "expected_keywords": ["china", "whatsapp", "google", "work", "access", "roaming", "unblocked", "vpn", "yes", "message"],
        "negative_keywords": []
    },

    # =========================================================================
    # 2. COMPATIBILITY AND INSTALLATION (6 Scenarios)
    # =========================================================================
    {
        "id": "COMPAT_01",
        "category": "Compatibility and installation",
        "customer_scenario": "The customer wants to buy a plan, but their device may not support eSIM.",
        "expected_behavior": "Verify compatibility before payment and explain alternatives without pressure.",
        "prompt": "I want to buy a plan, but I'm not sure if my phone supports eSIM. How do I verify compatibility before paying?",
        "expected_keywords": ["compatibility", "support", "settings", "check", "eid", "sim manager", "esim", "verify"],
        "negative_keywords": []
    },
    {
        "id": "COMPAT_02",
        "category": "Compatibility and installation",
        "customer_scenario": "The phone supports eSIM but is locked to the customer's home carrier.",
        "expected_behavior": "Explain the restriction and direct the customer to the appropriate carrier support.",
        "prompt": "My phone supports eSIM, but it is carrier-locked to AT&T. Can I still install and use Eskimo eSIM?",
        "expected_keywords": ["locked", "carrier", "unlock", "support", "restriction", "contact", "home"],
        "negative_keywords": []
    },
    {
        "id": "COMPAT_03",
        "category": "Compatibility and installation",
        "customer_scenario": "The customer worries that installation will start the plan immediately.",
        "expected_behavior": "Explain installation and activation as separate steps using current plan rules.",
        "prompt": "If I install the Eskimo eSIM today before my trip, will my data plan start running or expiring immediately?",
        "expected_keywords": ["install", "activation", "start", "separate", "connect", "destination", "expiry", "immediately"],
        "negative_keywords": []
    },
    {
        "id": "COMPAT_04",
        "category": "Compatibility and installation",
        "customer_scenario": "The customer expects a QR code and cannot find one.",
        "expected_behavior": "Confirm the supported installation method and guide the customer step by step.",
        "prompt": "I purchased a plan and expected an email with a QR code, but I cannot find it. Where is my QR code?",
        "expected_keywords": ["app", "account", "install", "how to install", "qr", "direct", "code", "settings"],
        "negative_keywords": []
    },
    {
        "id": "COMPAT_05",
        "category": "Compatibility and installation",
        "customer_scenario": "The customer accidentally removed the Eskimo eSIM from their phone.",
        "expected_behavior": "Assess whether reinstallation is possible and escalate when account intervention is required.",
        "prompt": "I accidentally removed and deleted the Eskimo eSIM profile from my phone settings. What do I do now?",
        "expected_keywords": ["reinstall", "deleted", "remove", "support", "contact", "esim", "profile", "account"],
        "negative_keywords": []
    },
    {
        "id": "COMPAT_06",
        "category": "Compatibility and installation",
        "customer_scenario": "The customer purchased a new device and wants to move their service.",
        "expected_behavior": "Explain the supported transfer or reinstallation process and protect the account.",
        "prompt": "I purchased a new phone and want to move my Eskimo eSIM and remaining data from my old device. How do I do that?",
        "expected_keywords": ["new device", "phone", "transfer", "reinstall", "support", "one device", "account"],
        "negative_keywords": []
    },

    # =========================================================================
    # 3. CONNECTION ISSUES DURING TRAVEL (7 Scenarios)
    # =========================================================================
    {
        "id": "CONN_01",
        "category": "Connection issues during travel",
        "customer_scenario": "The customer has arrived in Tokyo but has no mobile data.",
        "expected_behavior": "Check line activation, data roaming, mobile data selection, and a safe connection reset.",
        "prompt": "I have arrived in Tokyo, but I have no mobile data on my Eskimo eSIM. How can I get connected?",
        "expected_keywords": ["roaming", "data roaming", "settings", "mobile data", "turn on", "restart", "airplane", "line"],
        "negative_keywords": []
    },
    {
        "id": "CONN_02",
        "category": "Connection issues during travel",
        "customer_scenario": "The phone displays signal bars, but pages do not load.",
        "expected_behavior": "Troubleshoot settings and network selection in a clear sequence.",
        "prompt": "My phone displays signal bars with Eskimo, but web pages and apps do not load. What should I check?",
        "expected_keywords": ["roaming", "apn", "network", "restart", "settings", "selection", "troubleshoot"],
        "negative_keywords": []
    },
    {
        "id": "CONN_03",
        "category": "Connection issues during travel",
        "customer_scenario": "The customer expects constant 5G but is receiving 4G or slower speeds.",
        "expected_behavior": "Set expectations, gather useful diagnostics, and avoid guaranteeing a specific speed.",
        "prompt": "I expected constant 5G speeds, but I am receiving 4G or slower speeds. Why am I not getting 5G?",
        "expected_keywords": ["5g", "4g", "lte", "speed", "coverage", "partner", "network", "location", "device"],
        "negative_keywords": []
    },
    {
        "id": "CONN_04",
        "category": "Connection issues during travel",
        "customer_scenario": "Service works in central Tokyo but drops underground or outside the city.",
        "expected_behavior": "Explain environmental and partner network limitations and suggest practical next steps.",
        "prompt": "Service works in central Tokyo, but data drops completely underground in the subway and outside the city.",
        "expected_keywords": ["underground", "subway", "signal", "coverage", "network", "manual", "search", "surface", "partner"],
        "negative_keywords": []
    },
    {
        "id": "CONN_05",
        "category": "Connection issues during travel",
        "customer_scenario": "The customer's primary SIM used roaming data.",
        "expected_behavior": "Show empathy, correct dual SIM settings, and avoid accepting unverified responsibility.",
        "prompt": "My primary SIM ended up using roaming data and my home carrier billed me! How do I prevent this?",
        "expected_keywords": ["roaming", "primary", "switching", "cellular data switching", "settings", "default", "eskimo", "dual sim"],
        "negative_keywords": []
    },
    {
        "id": "CONN_06",
        "category": "Connection issues during travel",
        "customer_scenario": "Phone data works, but the customer cannot connect a laptop.",
        "expected_behavior": "Confirm plan support and troubleshoot hotspot settings on the device.",
        "prompt": "Mobile data works on my phone, but my laptop cannot connect to my personal hotspot.",
        "expected_keywords": ["hotspot", "tethering", "laptop", "settings", "support", "password", "band", "apn"],
        "negative_keywords": []
    },
    {
        "id": "CONN_07",
        "category": "Connection issues during travel",
        "customer_scenario": "The customer is lost, stressed, and needs directions quickly.",
        "expected_behavior": "Prioritize the shortest recovery steps and add detail only after connection returns.",
        "prompt": "I am lost and stressed right now, and my phone has no connection to load map directions! What is the fastest fix?",
        "expected_keywords": ["roaming", "airplane mode", "restart", "wifi", "turn on", "quick", "step", "first"],
        "negative_keywords": []
    },

    # =========================================================================
    # 4. USAGE BALANCE AND PLANS (6 Scenarios)
    # =========================================================================
    {
        "id": "USAGE_01",
        "category": "Usage balance and plans",
        "customer_scenario": "The customer believes their data was consumed too quickly.",
        "expected_behavior": "Review common background usage, inspect device consumption, and avoid assumptions.",
        "prompt": "I believe my 1GB data plan was consumed way too quickly in just a few hours. Did Eskimo miscount my usage?",
        "expected_keywords": ["background", "consumption", "usage", "settings", "apps", "sync", "video", "check"],
        "negative_keywords": []
    },
    {
        "id": "USAGE_02",
        "category": "Usage balance and plans",
        "customer_scenario": "The customer asks what happens to remaining fixed data.",
        "expected_behavior": "Explain the applicable no expiry rules and how the balance can be used later.",
        "prompt": "What happens to my remaining fixed data after my current trip ends?",
        "expected_keywords": ["no expiry", "expire", "remaining", "balance", "future", "keep", "later", "valid"],
        "negative_keywords": []
    },
    {
        "id": "USAGE_03",
        "category": "Usage balance and plans",
        "customer_scenario": "The customer wants to share remaining fixed data.",
        "expected_behavior": "Confirm eligibility and guide the transfer without exposing account information.",
        "prompt": "I want to share my remaining fixed data with a friend. How can I transfer data to another user?",
        "expected_keywords": ["transfer", "share", "friend", "app", "phone number", "data", "send"],
        "negative_keywords": []
    },
    {
        "id": "USAGE_04",
        "category": "Usage balance and plans",
        "customer_scenario": "The customer bought a country plan for the wrong destination.",
        "expected_behavior": "Check whether the plan was used before explaining the remedy or escalation path.",
        "prompt": "I accidentally bought a country plan for Japan instead of South Korea. Can I change it?",
        "expected_keywords": ["unused", "wrong", "support", "contact", "destination", "plan", "exchange", "refund"],
        "negative_keywords": []
    },
    {
        "id": "USAGE_05",
        "category": "Usage balance and plans",
        "customer_scenario": "The customer assumes unlimited means unlimited full speed data.",
        "expected_behavior": "Explain any daily high speed allowance and reduced speed threshold in plain language.",
        "prompt": "Does an Unlimited plan mean unlimited full speed data without any daily limits or slowdowns?",
        "expected_keywords": ["unlimited", "high speed", "speed", "allowance", "reduced", "fair usage", "fup", "daily", "threshold"],
        "negative_keywords": []
    },
    {
        "id": "USAGE_06",
        "category": "Usage balance and plans",
        "customer_scenario": "The customer says their plan started earlier than expected.",
        "expected_behavior": "Investigate the activation trigger and connection history before drawing conclusions.",
        "prompt": "My plan shows as started earlier than expected before I arrived at my travel destination. Why did it start?",
        "expected_keywords": ["activation", "activate", "activated", "trigger", "connect", "supported", "network", "roaming", "destination", "turned on"],
        "negative_keywords": []
    },
    {
        "id": "USAGE_07",
        "category": "Usage balance and plans",
        "customer_scenario": "The customer has both a local country plan (Singapore) and world data, asking about consumption priority.",
        "expected_behavior": "Explain that Eskimo automatically prioritizes local country data before consuming world/global data without manual configuration.",
        "prompt": "I am travelling to Singapore. I have Singapore data & some world data. How do I ensure I use the Singapore data while in Singapore?",
        "expected_keywords": ["automatic", "priority", "singapore", "local", "world", "global", "first", "consume", "use"],
        "negative_keywords": []
    },

    # =========================================================================
    # 5. CASHBACK AND TRAVEL BOOKINGS (9 Scenarios)
    # =========================================================================
    {
        "id": "CASHBACK_01",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The customer does not understand how a partner booking earns cashback.",
        "expected_behavior": "Explain partner selection, tracked booking, validation, and account credit.",
        "prompt": "I don't understand how a partner booking earns cashback. How does Eskimo cashback work?",
        "expected_keywords": ["partner", "booking", "app", "link", "track", "cashback", "credit", "completed"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_02",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The customer visited Klook directly instead of starting through Eskimo.",
        "expected_behavior": "Explain why tracking may be missing without blame or a promise of manual credit.",
        "prompt": "I visited Klook directly and booked a tour instead of starting through Eskimo. Can I still claim cashback?",
        "expected_keywords": ["direct", "track", "eskimo", "link", "click", "require", "before", "booking"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_03",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The customer booked yesterday and cannot see it under Cashback status.",
        "expected_behavior": "Explain the tracking window and when support should investigate.",
        "prompt": "I booked a hotel yesterday through Eskimo, but I cannot see it under my Cashback status yet.",
        "expected_keywords": ["hours", "tracking", "window", "days", "partner", "pending", "support", "appear", "status"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_04",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The customer made two transactions without returning to Eskimo between them.",
        "expected_behavior": "Explain the click through requirement for each transaction and check partner terms.",
        "prompt": "I made two separate hotel bookings on Agoda after clicking through from Eskimo once. Did both earn cashback?",
        "expected_keywords": ["click", "each", "separate", "transaction", "return", "partner", "track"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_05",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The trip ended recently, but cashback has not been issued.",
        "expected_behavior": "Explain validation and the 60 to 120 day timeframe without promising an exact date.",
        "prompt": "My trip ended recently, but my cashback has not been issued yet. When will it be credited?",
        "expected_keywords": ["validation", "60", "120", "days", "completed", "pending", "partner", "stay"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_06",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The booking was cancelled, exchanged, or issued a new booking ID.",
        "expected_behavior": "Explain eligibility respectfully and point to the relevant partner terms.",
        "prompt": "My flight booking was cancelled and rebooked with a new booking ID. Am I still eligible for cashback?",
        "expected_keywords": ["cancelled", "rebook", "eligibility", "terms", "partner", "new", "original"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_07",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The credited amount is below the customer's calculation.",
        "expected_behavior": "Explain possible exclusions such as taxes, fees, ineligible items, and exchange rates.",
        "prompt": "The cashback credited to my account is below my calculation. Why is it lower than expected?",
        "expected_keywords": ["tax", "fee", "rate", "exclude", "net", "exchange", "calculation", "room rate"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_08",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The customer wants to apply cashback to an Eskimo data plan.",
        "expected_behavior": "Guide checkout and explain verified restrictions or balance requirements.",
        "prompt": "Can I apply my earned cashback balance to purchase an Eskimo data plan?",
        "expected_keywords": ["cashback", "data plan", "balance", "wallet", "checkout", "pay", "purchase"],
        "negative_keywords": []
    },
    {
        "id": "CASHBACK_09",
        "category": "Cashback and travel bookings",
        "customer_scenario": "The customer prefers a bank withdrawal.",
        "expected_behavior": "Explain only verified availability, thresholds, supported locations, and processing times.",
        "prompt": "I prefer a bank withdrawal for my cashback. What are the withdrawal thresholds and processing times?",
        "expected_keywords": ["withdraw", "minimum", "25", "bank", "threshold", "processing", "time", "method"],
        "negative_keywords": []
    },

    # =========================================================================
    # 6. COMPLAINTS AND DIFFICULT CONVERSATIONS (7 Scenarios)
    # =========================================================================
    {
        "id": "COMPLAINT_01",
        "category": "Complaints and difficult conversations",
        "customer_scenario": "The customer requests a full refund after using part of the plan.",
        "expected_behavior": "Acknowledge the concern, check usage, and explain the applicable policy accurately.",
        "prompt": "I want a full refund for my data plan even though I used part of it. Can I get a full refund?",
        "expected_keywords": ["refund", "used", "policy", "usage", "support", "acknowledge", "unused"],
        "negative_keywords": []
    },
    {
        "id": "COMPLAINT_02",
        "category": "Complaints and difficult conversations",
        "customer_scenario": "The customer has no connection before an important meeting.",
        "expected_behavior": "De-escalate, troubleshoot efficiently, and provide a clear escalation path.",
        "prompt": "I have no connection right before an important business meeting! I need help immediately!",
        "expected_keywords": ["roaming", "restart", "airplane", "settings", "support", "escalate", "urgent", "troubleshoot"],
        "negative_keywords": []
    },
    {
        "id": "COMPLAINT_03",
        "category": "Complaints and difficult conversations",
        "customer_scenario": "The customer wants assurance that service will work everywhere.",
        "expected_behavior": "Explain dependence on local networks and avoid making guarantees.",
        "prompt": "Can you give me assurance that your eSIM service will work everywhere I go?",
        "expected_keywords": ["guarantee", "depend", "local", "network", "coverage", "terrain", "partner", "cannot"],
        "negative_keywords": []
    },
    {
        "id": "COMPLAINT_04",
        "category": "Complaints and difficult conversations",
        "customer_scenario": "The customer previously saw a lower promotional price.",
        "expected_behavior": "Explain the current offer without inventing a discount or blaming the customer.",
        "prompt": "I previously saw a lower promotional price for this plan last week. Can you give me that lower price?",
        "expected_keywords": ["price", "promotion", "current", "offer", "limited", "rate", "discount"],
        "negative_keywords": []
    },
    {
        "id": "COMPLAINT_05",
        "category": "Complaints and difficult conversations",
        "customer_scenario": "A creator asks an agent to provide complimentary data.",
        "expected_behavior": "Avoid unauthorized commitments and route the request to the appropriate team.",
        "prompt": "I am a content creator with 100k followers. Can you provide me with complimentary data in exchange for a shoutout?",
        "expected_keywords": ["partnership", "marketing", "team", "affiliate", "referral", "free", "contact"],
        "negative_keywords": []
    },
    {
        "id": "COMPLAINT_06",
        "category": "Complaints and difficult conversations",
        "customer_scenario": "The customer reports unfamiliar purchases or data transfers.",
        "expected_behavior": "Protect the account, limit disclosure, and escalate through the security process.",
        "prompt": "There are unfamiliar purchases and data transfers listed in my account that I did not do! Has my account been breached?",
        "expected_keywords": ["security", "protect", "support", "account", "investigate", "escalate", "password"],
        "negative_keywords": []
    },
    {
        "id": "COMPLAINT_07",
        "category": "Complaints and difficult conversations",
        "customer_scenario": "The customer struggles to follow technical instructions.",
        "expected_behavior": "Use one step at a time, avoid jargon, and confirm success before continuing.",
        "prompt": "I am struggling to follow technical instructions. Can you guide me through this simply without technical jargon?",
        "expected_keywords": ["step", "simple", "settings", "open", "help", "easy", "first"],
        "negative_keywords": []
    }
]


def get_scenarios_by_category(category_name: str) -> List[Dict[str, Any]]:
    """Filter scenarios by category name."""
    return [s for s in AI_AGENT_SCENARIOS if s["category"].lower() == category_name.lower()]


def get_all_categories() -> List[str]:
    """Get list of distinct category names in order."""
    seen = []
    for s in AI_AGENT_SCENARIOS:
        if s["category"] not in seen:
            seen.append(s["category"])
    return seen

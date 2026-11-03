from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- CONFIGURATIE ---
# Verander dit wachtwoord voordat je de website live zet!
ADMIN_PASSWORD = "admin1234"

# Centrale database met populaire Roblox items
ITEM_DATABASE = {
    # --- ADOPT ME ---
    "shadow_dragon": {"name": "Shadow Dragon", "value": 1000, "category": "Adopt Me"},
    "bat_dragon": {"name": "Bat Dragon", "value": 920, "category": "Adopt Me"},
    "frost_dragon": {"name": "Frost Dragon", "value": 750, "category": "Adopt Me"},
    "giraffe": {"name": "Giraffe", "value": 680, "category": "Adopt Me"},
    "owl": {"name": "Owl", "value": 480, "category": "Adopt Me"},
    "parrot": {"name": "Parrot", "value": 410, "category": "Adopt Me"},
    "evil_unicorn": {"name": "Evil Unicorn", "value": 320, "category": "Adopt Me"},
    "crow": {"name": "Crow", "value": 310, "category": "Adopt Me"},
    
    # --- MURDER MYSTERY 2 (MM2) ---
    "harvester": {"name": "Harvester (Gun)", "value": 1250, "category": "Murder Mystery 2"},
    "corrupt_knife": {"name": "Corrupt (Knife)", "value": 900, "category": "Murder Mystery 2"},
    "candleflame": {"name": "Candleflame (Knife)", "value": 420, "category": "Murder Mystery 2"},
    "icepiercer": {"name": "Icepiercer (Gun)", "value": 1100, "category": "Murder Mystery 2"},
    "makeshift": {"name": "Makeshift (Gun)", "value": 650, "category": "Murder Mystery 2"},
    "elderwood_scythe": {"name": "Elderwood Scythe", "value": 220, "category": "Murder Mystery 2"},
    "chroma_fang": {"name": "Chroma Fang", "value": 180, "category": "Murder Mystery 2"},

    # --- BLOX FRUITS ---
    "kitsune_fruit": {"name": "Kitsune Physical Fruit", "value": 1500, "category": "Blox Fruits"},
    "leopard_fruit": {"name": "Leopard Physical Fruit", "value": 800, "category": "Blox Fruits"},
    "dragon_fruit": {"name": "Dragon Physical Fruit", "value": 1100, "category": "Blox Fruits"},
    "dough_fruit": {"name": "Dough Physical Fruit", "value": 450, "category": "Blox Fruits"},
    "t_rex_fruit": {"name": "T-Rex Physical Fruit", "value": 400, "category": "Blox Fruits"},
    "spirit_fruit": {"name": "Spirit Physical Fruit", "value": 250, "category": "Blox Fruits"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roblox Ultimate Trade Calculator & Database</title>
    <style>
        :root {
            --bg-color: #0f0f12;
            --card-color: #16161c;
            --accent-color: #3498db;
            --success-color: #2ecc71;
            --danger-color: #e74c3c;
            --text-color: #ffffff;
            --border-color: #262630;
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 30px; }
        h1 { margin-bottom: 5px; color: var(--accent-color); font-size: 2.5rem; }
        
        .tabs { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; }
        .tab-btn {
            background-color: var(--card-color); color: white; border: 1px solid var(--border-color);
            padding: 10px 25px; border-radius: 20px; cursor: pointer; font-weight: bold;
        }
        .tab-btn.active { background-color: var(--accent-color); border-color: var(--accent-color); }
        .page { display: none; }
        .page.active { display: block; }

        .trade-zone { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px; }
        @media (max-width: 768px) { .trade-zone { grid-template-columns: 1fr; } }
        .trade-box { background-color: var(--card-color); padding: 25px; border-radius: 14px; border: 2px solid var(--border-color); position: relative; }
        .search-container { position: relative; margin-bottom: 15px; }
        input, select {
            width: 100%; padding: 14px; box-sizing: border-box; border-radius: 8px; border: 2px solid var(--border-color);
            background-color: #202026; color: white; font-size: 16px;
        }
        input:focus, select:focus { border-color: var(--accent-color); outline: none; }
        
        .autocomplete-suggestions {
            position: absolute; top: 100%; left: 0; right: 0; background-color: #202026; border: 1px solid var(--border-color);
            border-radius: 0 0 8px 8px; max-height: 250px; overflow-y: auto; z-index: 1000; display: none; box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
        }
        .suggestion-item { padding: 12px; cursor: pointer; border-bottom: 1px solid #2b2b36; text-align: left; }
        .suggestion-item:hover { background-color: var(--accent-color); }
        
        .item-list { text-align: left; list-style: none; padding: 0; margin-top: 15px; }
        .item-list li {
            padding: 12px; background: #1c1c24; margin-bottom: 8px; border-radius: 6px;
            display: flex; justify-content: space-between; align-items: center; border: 1px solid var(--border-color);
        }
        .remove-btn { color: var(--danger-color); cursor: pointer; background: none; border: none; font-size: 18px; }
        .action-btn {
            width: 100%; padding: 16px; border-radius: 8px; border: none; background-color: var(--accent-color);
            color: white; font-size: 18px; cursor: pointer; font-weight: bold; transition: 0.2s;
        }
        .action-btn:hover { background-color: #2980b9; }

        #result-display {
            background-color: var(--card-color); padding: 35px; border-radius: 14px;
            margin-top: 25px; display: none; border: 2px solid var(--border-color); text-align: center;
        }
        #outcome-badge { font-size: 36px; font-weight: bold; margin: 15px 0; display: inline-block; padding: 12px 40px; border-radius: 10px; color: white; }
        
        /* Admin Login & Layout */
        #admin-auth { max-width: 400px; margin: 50px auto; padding: 30px; background: var(--card-color); border-radius: 12px; border: 2px solid var(--border-color); }
        .admin-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
        @media (max-width: 768px) { .admin-grid { grid-template-columns: 1fr; } }
        .admin-table { width: 100%; border-collapse: collapse; margin-top: 15px; text-align: left; }
        .admin-table th, .admin-table td { padding: 12px; border-bottom: 1px solid var(--border-color); }
        .admin-table th { background-color: #202026; }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Roblox Trade Matrix</h1>
        <p>Real-time Win / Fair / Lose Waardeberekening</p>
    </header>

    <div class="tabs">
        <button id="tab-calc" class="tab-btn active" onclick="switchPage('calculator')">🧮 Calculator</button>
        <button id="tab-admin" class="tab-btn" onclick="switchPage('admin')">⚙️ Admin Dashboard</button>
    </div>

    <!-- CALCULATOR PAGE -->
    <div id="calculator-page" class="page active">
        <div class="trade-zone">
            <div class="trade-box">
                <h2>Jouw Items (Your Offer)</h2>
                <div class="search-container">
                    <input type="text" id="your-search" placeholder="Zoek een item..." oninput="showSuggestions('your')">
                    <div id="your-suggestions" class="autocomplete-suggestions"></div>
                </div>
                <ul id="your-list" class="item-list"></ul>
            </div>

            <div class="trade-box">
                <h2>Hun Items (Their Offer)</h2>
                <div class="search-container">
                    <input type="text" id="their-search" placeholder="Zoek een item..." oninput="showSuggestions('their')">
                    <div id="their-suggestions" class="autocomplete-suggestions"></div>
                </div>
                <ul id="their-list" class="item-list"></ul>
            </div>
        </div>

        <button class="action-btn" onclick="processTrade()">Bereken WFL Uitkomst</button>

        <div id="result-display">
            <h3>Resultaat van de Ruil</h3>
            <p>Jouw Waarde: <span id="res-your-val" style="font-weight:bold; font-size: 20px; color:var(--accent-color);">0</span></p>
            <p>Hun Waarde: <span id="res-their-val" style="font-weight:bold; font-size: 20px; color:var(--success-color);">0</span></p>
            <div id="outcome-badge">FAIR</div>
        </div>
    </div>

    <!-- ADMIN AUTH PAGE (LOGIN) -->
    <div id="admin-auth-page" class="page">
        <div id="admin-auth">
            <h3>Admin Toegang Vereist</h3>
            <p style="color: #888; font-size: 14px;">Voer het beheerderswachtwoord in om wijzigingen aan te brengen.</p>
            <input type="password" id="admin-password-input" placeholder="Wachtwoord..." style="margin-bottom: 15px;">
            <button class="action-btn" onclick="verifyAdminPassword()">Inloggen</button>
        </div>
    </div>

    <!-- ADMIN PANEL CONTENT PAGE -->
    <div id="admin-content-page" class="page">
        <div class="admin-grid">
            <div class="trade-box" style="height: fit-content;">
                <h3>Nieuw Item Toevoegen</h3>
                <div style="margin-bottom: 12px;">
                    <label>Item Naam</label>
                    <input type="text" id="admin-name" placeholder="Bijv. Neon Cow">
                </div>
                <div style="margin-bottom: 12px;">
                    <label>Waarde (Punten)</label>
                    <input type="number" id="admin-value" placeholder="Bijv. 150">
                </div>
                <div style="margin-bottom: 20px;">
                    <label>Game Categorie</label>
                    <select id="admin-category">

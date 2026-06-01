def inject_custom_styles():
    """Returns custom CSS to style Streamlit buttons and layout radially around a central avatar."""
    return """
    <style>
        /* Base color scheme and glassmorphism overrides */
        .stApp {
            background: linear-gradient(135deg, #090615 0%, #0d0b21 50%, #05040a 100%);
            font-family: 'Outfit', sans-serif;
            color: #f3f4f6;
        }

        /* Title styling */
        .main-title {
            text-align: center;
            background: linear-gradient(90deg, #a78bfa 0%, #38bdf8 50%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.5rem;
            font-weight: 900;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
            filter: drop-shadow(0 0 15px rgba(167, 139, 250, 0.3));
        }

        .subtitle {
            text-align: center;
            color: #9ca3af;
            font-size: 1.1rem;
            margin-bottom: 3rem;
            font-weight: 300;
        }

        /* Central Avatar styling */
        .avatar-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 40px auto;
            position: relative;
            width: 140px;
            height: 140px;
        }

        .avatar-pulsing {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            background: rgba(139, 92, 246, 0.15);
            border: 2px solid #8b5cf6;
            box-shadow: 0 0 35px rgba(139, 92, 246, 0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 4rem;
            animation: pulse 2.5s infinite ease-in-out;
            transition: all 0.3s ease;
        }

        .avatar-pulsing:hover {
            box-shadow: 0 0 55px rgba(6, 182, 212, 0.8);
            border-color: #06b6d4;
            transform: scale(1.08);
        }

        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 30px rgba(139, 92, 246, 0.5); }
            50% { transform: scale(1.06); box-shadow: 0 0 50px rgba(6, 182, 212, 0.7); }
            100% { transform: scale(1); box-shadow: 0 0 30px rgba(139, 92, 246, 0.5); }
        }

        /* Styled Premium Card buttons (Launcher Game Selector buttons) */
        div.stButton > button {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #f3f4f6 !important;
            border-radius: 16px !important;
            padding: 18px 22px !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            backdrop-filter: blur(12px) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
            text-align: center !important;
            width: 100% !important;
        }

        div.stButton > button:hover {
            background: rgba(139, 92, 246, 0.15) !important;
            border-color: #8b5cf6 !important;
            box-shadow: 0 0 25px rgba(139, 92, 246, 0.4) !important;
            transform: translateY(-4px) scale(1.02) !important;
        }

        /* Side panels and containers */
        .glass-panel {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 24px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }

        .panel-header {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 15px;
            color: #a78bfa;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Standard base board container */
        .board-container {
            display: grid;
            gap: 8px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 20px;
            margin: 0 auto;
            max-width: 540px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
            transition: all 0.4s ease;
        }

        /* Chess Board UI Styles (Classic green/white Chess.com palette) */
        .chess-board-container {
            background: #252422 !important;
            border: 12px solid #31302d !important;
            box-shadow: 0 25px 50px rgba(0,0,0,0.8) !important;
        }

        /* Carrom Board UI Styles (High-fidelity varnished wood grain skeuomorphism) */
        .carrom-board-container {
            background: radial-gradient(circle, #eec787 30%, #cd9241 100%) !important;
            border: 16px solid #4a2a18 !important;
            box-shadow: inset 0 0 40px rgba(0,0,0,0.4), 0 25px 50px rgba(0,0,0,0.8) !important;
            border-radius: 32px !important;
            position: relative;
        }

        /* Reversi Board UI Styles (Lush Green Felt with thick borders) */
        .reversi-board-container {
            background: radial-gradient(circle, #277233 40%, #154b1d 100%) !important;
            border: 12px solid #2e1c0c !important;
            box-shadow: inset 0 0 30px rgba(0,0,0,0.6), 0 25px 50px rgba(0,0,0,0.8) !important;
        }

        /* Connect Four Board UI Styles (Glowing blue plastic vertical rack structure) */
        .connectfour-board-container {
            background: linear-gradient(180deg, #1565c0 0%, #0d47a1 100%) !important;
            border: 8px solid #0a3375 !important;
            box-shadow: 0 25px 40px rgba(0,0,0,0.7) !important;
            border-radius: 16px !important;
        }

        /* Go Board UI Styles (Premium golden Kaya wood grain) */
        .go-board-container {
            background: #e2b675 !important;
            border: 14px solid #b78a48 !important;
            box-shadow: inset 0 0 25px rgba(0,0,0,0.3), 0 25px 50px rgba(0,0,0,0.7) !important;
        }

        /* Air Hockey Board UI Styles (Hyper-futuristic neon rink stadium layout) */
        .airhockey-board-container {
            background: #111422 !important;
            border: 6px solid #29b6f6 !important;
            box-shadow: 0 0 35px rgba(41, 182, 246, 0.4), inset 0 0 20px rgba(0,0,0,0.8) !important;
            position: relative;
        }

        /* Hex Board UI Styles (Parallelogram offset alignment) */
        .hex-board-container {
            background: #141026 !important;
            border: 6px dashed #7c3aed !important;
            box-shadow: 0 20px 40px rgba(124, 58, 237, 0.25) !important;
        }

        /* Mancala Board UI Styles (Polished Mahogany Wood with dug cups) */
        .mancala-board-container {
            background: radial-gradient(circle, #6d391d 40%, #3e1b09 100%) !important;
            border: 10px solid #240e04 !important;
            box-shadow: inset 0 0 30px rgba(0,0,0,0.8), 0 20px 40px rgba(0,0,0,0.6) !important;
            border-radius: 28px !important;
        }

        /* Tiger Chess Board UI Styles (Symmetric grid wood board) */
        .tiger-board-container {
            background: #dfb170 !important;
            border: 12px solid #8d6232 !important;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.3), 0 20px 40px rgba(0,0,0,0.6) !important;
            border-radius: 20px !important;
        }

        /* Backgammon Board UI Styles (Polished walnut casework board) */
        .backgammon-board-container {
            background: radial-gradient(circle, #a16b47 30%, #5d351b 100%) !important;
            border: 14px solid #2e1405 !important;
            box-shadow: 0 25px 45px rgba(0,0,0,0.8) !important;
            border-radius: 24px !important;
        }
    </style>
    """

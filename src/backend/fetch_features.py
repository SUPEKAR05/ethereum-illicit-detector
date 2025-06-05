# === File: backend/fetch_features.py ===
import requests
from datetime import datetime
import joblib

ETHERSCAN_API_KEY = "7DNR18H7ASKXYSZNATBFRIPT4IZUDCNJ7U"

# Load the fitted label encoder
try:
    token_encoder = joblib.load("token_type_encoder.pkl")
except Exception as e:
    print("Warning: Token encoder not found.")
    token_encoder = None

def get_features_from_etherscan(address: str, token_encoder=None) -> list:
    def safe_div(x, y):
        return x / y if y else 0

    try:
        features = []

        # 1. ETH Balance
        bal_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
        bal_res = requests.get(bal_url).json()
        balance_eth = int(bal_res['result']) / 1e18 if bal_res['status'] == '1' else 0

        # 2. Normal transaction list
        tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}"
        tx_res = requests.get(tx_url).json()
        txs = tx_res['result'] if tx_res['status'] == '1' else []

        total_txs = len(txs)
        sent_txs = [tx for tx in txs if tx['from'].lower() == address.lower()]
        recv_txs = [tx for tx in txs if tx['to'].lower() == address.lower()]
        sent_count = len(sent_txs)
        recv_count = len(recv_txs)

        values_received = [int(tx['value']) / 1e18 for tx in recv_txs]
        values_sent = [int(tx['value']) / 1e18 for tx in sent_txs]
        times = [int(tx['timeStamp']) for tx in txs]

        time_diff_min = safe_div((int(times[-1]) - int(times[0])) / 60, total_txs) if len(times) > 1 else 0

        # Gas features
        gas_prices = [int(tx['gasPrice']) / 1e9 for tx in txs if 'gasPrice' in tx]
        gas_limits = [int(tx['gas']) for tx in txs if 'gas' in tx]
        gas_used = [int(tx['gasUsed']) for tx in txs if 'gasUsed' in tx]
        gas_fees = [g * l / 1e9 for g, l in zip(gas_prices, gas_limits)]

        # ERC20 token transactions
        erc_url = f"https://api.etherscan.io/api?module=account&action=tokentx&address={address}&startblock=0&endblock=999999999&sort=asc&apikey={ETHERSCAN_API_KEY}"
        erc_res = requests.get(erc_url).json()
        erc_txs = erc_res['result'] if erc_res['status'] == '1' else []

        erc_sent = [tx for tx in erc_txs if tx['from'].lower() == address.lower()]
        erc_recv = [tx for tx in erc_txs if tx['to'].lower() == address.lower()]
        erc_sent_val = [int(tx['value']) / 1e18 for tx in erc_sent]
        erc_recv_val = [int(tx['value']) / 1e18 for tx in erc_recv]

        # Token type encoding (new)
        most_sent_token = erc_sent[-1]['tokenName'] if erc_sent else "Unknown"
        most_recv_token = erc_recv[-1]['tokenName'] if erc_recv else "Unknown"

        sent_encoded = token_encoder.transform([most_sent_token])[0] if token_encoder and most_sent_token in token_encoder.classes_ else 0
        recv_encoded = token_encoder.transform([most_recv_token])[0] if token_encoder and most_recv_token in token_encoder.classes_ else 0

        # Assemble known features
        features.extend([
            balance_eth, total_txs, time_diff_min, 0, 0, sent_count, recv_count, 0, 0,
            min(values_received, default=0), max(values_received, default=0), safe_div(sum(values_received), len(values_received)),
            min(values_sent, default=0), max(values_sent, default=0), safe_div(sum(values_sent), len(values_sent)),
            sum(values_sent), sum(values_received), len(erc_txs), sum(erc_recv_val), sum(erc_sent_val),
            len(set(tx['to'] for tx in erc_sent)), len(set(tx['from'] for tx in erc_recv)), 0, 0,
            min(erc_recv_val, default=0), max(erc_recv_val, default=0), safe_div(sum(erc_recv_val), len(erc_recv_val)),
            min(erc_sent_val, default=0), max(erc_sent_val, default=0), safe_div(sum(erc_sent_val), len(erc_sent_val)),
            len(set(tx['tokenName'] for tx in erc_sent)), len(set(tx['tokenName'] for tx in erc_recv)),
            sent_encoded, recv_encoded,
            safe_div(sum(gas_prices), len(gas_prices)), safe_div(sum(gas_limits), len(gas_limits)),
            safe_div(sum(gas_used), len(gas_used)), safe_div(sum(gas_fees), len(gas_fees)),
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ])

        return features[:50] if len(features) >= 50 else features + [0.0] * (50 - len(features))

    except Exception as e:
        print("[Feature extraction error]", e)
        return [0.0] * 50

import requests
import json

# Test various wallet addresses
wallets = [
    '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
    '0xABCDEFABCDEFABCDEFABCDEFABCDEFABCDEFABCD',
    '0x0000000000000000000000000000000000000001',
]

for wallet in wallets:
    print(f'\nTesting wallet: {wallet} (len={len(wallet)})')
    try:
        r = requests.post(f'http://127.0.0.1:8000/loan/request?wallet_address={wallet}&amount=50000')
        data = r.json()
        print(f'Status: {r.status_code}')
        print(f'Approved: {data.get("approved")}')
        print(f'DB ID: {data.get("db_loan_id")}')
        print(f'Persistence: {data.get("pipeline_status", {}).get("persistence")}')
    except Exception as e:
        print(f'Error: {e}')

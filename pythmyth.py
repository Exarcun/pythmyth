import logging
import subprocess
from web3 import Web3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider('INFURA_ID'))

def analyze_contract_with_mythril(contract_address):
    logging.info(f'Analyzing contract {contract_address} with Mythril...')
    try:
        # Replace 'myth' with the path to your Mythril installation if not in PATH
        cmd = ['myth', 'analyze', '--execution-timeout', '600', '--max-depth', '20', '--address', contract_address]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Write result to a file named after the contract address
        with open(f'{contract_address}.txt', 'w') as file:
            file.write(result.stdout)
        
        logging.info(f'Analysis for contract {contract_address} written to {contract_address}.txt')

    except Exception as e:
        logging.error(f'Error analyzing contract {contract_address}: {e}')

def handle_transaction(tx):
    if tx['to'] is None:  # Contract creation transaction
        logging.info(f'Found contract creation transaction: {tx["hash"].hex()}')
        receipt = w3.eth.get_transaction_receipt(tx['hash'])
        contract_address = receipt['contractAddress']
        if contract_address:
            code = w3.eth.get_code(Web3.to_checksum_address(contract_address))
            if code != '0x':  # It's a contract
                analyze_contract_with_mythril(Web3.to_checksum_address(contract_address))
            else:
                logging.info(f'Address {contract_address} is not a contract.')
        else:
            logging.warning('No contract address found in the transaction receipt.')

def main():
    block_filter = w3.eth.filter('latest')
    logging.info('Starting to monitor for contract creation transactions...')
    while True:
        for block_hash in block_filter.get_new_entries():
            block = w3.eth.get_block(block_hash, full_transactions=True)
            logging.info(f'Checking new block: {block["number"]}')
            for tx in block.transactions:
                handle_transaction(tx)

if __name__ == '__main__':
    main()


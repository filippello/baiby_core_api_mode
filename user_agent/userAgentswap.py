from pathlib import Path
import os
import dotenv
import logging
from multiversx_sdk import Account, DevnetEntrypoint, Transaction, Address, ProxyNetworkProvider

dotenv.load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
NETWORK_URL = "https://devnet-gateway.multiversx.com"
XEXCHANGE_ROUTER = "erd1qqqqqqqqqqqqqpgq6wg9syswgy09knrw2tg6q7qew2n8zjwx0n4s377sfe"

# Token identifiers en formato hex
USDC_HEX = "555344432d333530633465"  # USDC-350c4e en hex
MEX_HEX = "4d45582d613635396430"      # MEX-a659d0 en hex
SPK_HEX = "53504b2d383136313865"      # SPK-816185 en hex

provider = ProxyNetworkProvider(NETWORK_URL)

def create_account():
    entrypoint = DevnetEntrypoint()
    account = Account.new_from_keystore(
        file_path=Path("user_agent/wallet.json"),
        password=os.getenv("WALLET_PASSWORD")
    )
    account_on_network = provider.get_account(account.address)
    account.nonce = account_on_network.nonce
    return account

def perform_swap():
    try:
        account = create_account()
        logger.info(f"Account loaded: {account.address}")
        
        # Data exacta de la transacción exitosa en una sola línea
        data = "composeTasks@0000000b555344432d3335306334650000000000000000000000020a19@@@03@0000002000000000000000000500139ed7ae4aa03792e6bcb332394a40fe746eefa47ceb0000001473776170546f6b656e734669786564496e7075740000000a4d45582d6136353964300000000905d29cf5762d1a21b400000020000000000000000005003a7c122cb42aa83c3e90fac39412de71036d77dc7ceb0000001473776170546f6b656e734669786564496e7075740000000a53504b2d383136313865000000082b4659d0d1000c9d0000002000000000000000000500333e284cdbd08725558faf59426b1f757221e6fa7ceb0000001473776170546f6b656e734669786564496e7075740000000b555344432d333530633465000000020a10"

        tx = Transaction(
            nonce=account.nonce,
            value=int(0.0001 * 10**18),
            sender=account.address,
            receiver=Address.from_bech32(XEXCHANGE_ROUTER),
            gas_limit=60000000,
            data=data.encode(),
            chain_id="D",
            version=1
        )

        tx.signature = account.sign_transaction(tx)
        tx_hash = provider.send_transaction(tx)
        
        logger.info(f"Swap transaction sent! Hash: {tx_hash}")
        return tx_hash

    except Exception as e:
        logger.error(f"Error performing swap: {e}")
        raise

if __name__ == "__main__":
    perform_swap()

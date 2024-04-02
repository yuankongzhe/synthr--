
from time import sleep
from web3 import Web3
def init_web3(ethereum_node_url):
    """初始化Web3连接"""
    
    web3 = Web3(Web3.HTTPProvider(ethereum_node_url))
    assert web3.is_connected(), "Cannot connect to the Ethereum node"
    return web3

def erc20_abi():
    """Return the ERC20 token contract ABI."""
    return [
        {
            "constant": False,
            "inputs": [
                {
                    "name": "_amount",
                    "type": "uint256"
                },
            ],
            "name": "faucetToken",
            "outputs": [
                {
                    "name": "",
                    "type": "bool"
                }
            ],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
        "constant": False,
        "inputs": [
        {
            "name": "_collateralKey",
            "type": "bytes32"
        },
        {
            "name": "_collateralAmount",
            "type": "uint256"
        },
        {
            "name": "_synthToMint",
            "type": "uint256"
        },
        {
            "name": "_bridgeName",
            "type": "bytes32"
        },
        {
            "name": "_destChainId",
            "type": "uint16"
        },
        {
            "name": "erc20Payment",
            "type": "bool"
        }
        ],
        "name": "issueSynths",
        "outputs": [
        {
            "name": "",
            "type": "bool"
        }
            ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    ]
def faucetToken_erc20(web3, contract_address, from_address, amount, private_key,gas_price):
    """faucetToken ERC20 token."""
    contract_address = web3.to_checksum_address(contract_address)
    from_address = web3.to_checksum_address(from_address)

    contract = web3.eth.contract(address=contract_address, abi=erc20_abi())

    value = web3.to_wei(amount, 'ether')  # Assuming the token uses 18 decimal places
    chain_id = web3.eth.chain_id
    nonce = web3.eth.get_transaction_count(from_address)
    suggested_gas_price =web3.to_wei(gas_price, 'gwei') 
    estimated_gas = contract.functions.faucetToken(value).estimate_gas({
        'from': from_address
    })
    print(f'from address: {from_address}')

    for i in range(10):
        print(f'now nonce is {nonce}, send on chain {chain_id} with gas price {suggested_gas_price}, gas {estimated_gas}')
        tx = {
            'nonce': nonce,
            'to': contract_address,
            'value': 0,
            'gas': estimated_gas,
            'gasPrice': suggested_gas_price,
            'chainId': chain_id,
            'data': contract.encodeABI(fn_name='faucetToken', args=[value]),
        }
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f'send tx :{web3.to_hex(tx_hash)}')
            return web3.to_hex(tx_hash)
        except ValueError as e:
            # 检查是否是特定的nonce错误
            if isinstance(e.args[0], dict) and e.args[0].get('code') == -32000 and 'invalid nonce' in e.args[0].get('message'):
                print("Nonce too low, incrementing nonce and retrying...")
                nonce += 1  # 增加nonce并重试
            elif isinstance(e.args[0], dict) and e.args[0].get('code') == -32000 and 'nonce too low' in e.args[0].get('message'):
                print("Nonce too low, incrementing nonce and retrying...")
                nonce += 1  # 增加nonce并重试  
            else:
                # 如果是其他ValueError，则抛出异常
                raise e

def issue_synths(web3, contract_address, from_address, collateral_key, collateral_amount, synth_to_mint, bridge_name, dest_chain_id, erc20_payment, private_key):
    """Issue Synths using the issueSynths function."""
    contract_address = web3.to_checksum_address(contract_address)
    from_address = web3.to_checksum_address(from_address)

    contract = web3.eth.contract(address=contract_address, abi=erc20_abi())

    chain_id = web3.eth.chain_id
    nonce = web3.eth.get_transaction_count(from_address)
    suggested_gas_price = web3.to_wei('5', 'gwei')
    estimated_gas = contract.functions.issueSynths(
        collateral_key,
        collateral_amount,
        synth_to_mint,
        bridge_name,
        dest_chain_id,
        erc20_payment
    ).estimate_gas({
        'from': from_address
    })

    print(f'from address: {from_address}')

    for i in range(10):
        print(f'now nonce is {nonce}, send on chain {chain_id} with gas price {suggested_gas_price}, gas {estimated_gas}')
        tx = {
            'nonce': nonce,
            'to': contract_address,
            'value': 0,
            'gas': estimated_gas,
            'gasPrice': suggested_gas_price,
            'chainId': chain_id,
            'data': contract.encodeABI(fn_name='issueSynths', args=[
                collateral_key,
                collateral_amount,
                synth_to_mint,
                bridge_name,
                dest_chain_id,
                erc20_payment
            ]),
        }
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        try:
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f'send tx :{web3.to_hex(tx_hash)}')
            return web3.to_hex(tx_hash)
        except ValueError as e:
            if isinstance(e.args[0], dict) and e.args[0].get('code') == -32000 and 'invalid nonce' in e.args[0].get('message'):
                print("Nonce too low, incrementing nonce and retrying...")
                nonce += 1
            elif isinstance(e.args[0], dict) and e.args[0].get('code') == -32000 and 'nonce too low' in e.args[0].get('message'):
                print("Nonce too low, incrementing nonce and retrying...")
                nonce += 1
            elif isinstance(e.args[0], dict) and e.args[0].get('code') == -32000 and 'nonce too high' in e.args[0].get('message'):
                print("Nonce too high, decrementing nonce and retrying...")
                nonce -= 1
            else:
                print(e)
                print('now pause 10 seconds and continue')
                sleep(10)

if __name__ == "__main__":            
    arb_rpc = 'https://sepolia-rollup.arbitrum.io/rpc'
    token_contract_address = '0x9aa40cc99973d8407a2ae7b2237d26e615ecafd2'
    web3_instance = init_web3(arb_rpc)
    #--------------------------------------------
    main_key= '0x00000000000000000000000000' #Set your private key here
    main_wallet_address = '0x111111111111111111111111111' #Set your wallet address here
    #--------------------------------------------
    for _ in range(20):
        try:
            faucetToken_erc20(web3_instance, token_contract_address,main_wallet_address, 500000, main_key,'5')
        except Exception as e:
            print(e)
            continue
    for _ in range(3000):
        issue_synths(
            web3=web3_instance, 
            contract_address='0xe0875cbd144fe66c015a95e5b2d2c15c3b612179', 
            from_address=main_wallet_address, 
            collateral_key='0x5553445400000000000000000000000000000000000000000000000000000000', 
            collateral_amount=100000000000000000000, 
            synth_to_mint=0, 
            bridge_name='0x4c617965725a65726f0000000000000000000000000000000000000000000000', 
            dest_chain_id=0, 
            erc20_payment=False, 
            private_key=main_key
            )
        sleep(1)


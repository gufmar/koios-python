#!/usr/bin/env python

import json
import requests


def get_blocks():
    """Get summarised details about all blocks (paginated - latest first)"""
    blocks = requests.get("https://api.koios.rest/api/v0/blocks")
    blocks = json.loads(blocks.content)
    return blocks


def get_block_info(block_hash):
    """Get detailed information about a specific block"""
    format = {"_block_hashes":[block_hash]}
    block = requests.post("https://api.koios.rest/api/v0/block_info", json = format)
    block = json.loads(block.content)[0]
    return block


def get_block_txs(block_hash):
    """Get a list of all transactions included in a provided block"""
    block = requests.get("https://api.koios.rest/api/v0/block_txs?_block_hash="+str(block_hash))
    block = json.loads(block.content)[0]
    return 
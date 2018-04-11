import binascii
import requests
import json
import ipfsapi
import os
import multiprocessing
import datetime
import sys
import hashlib
from time import gmtime, strftime
from flask import Blueprint, render_template, jsonify, current_app as app, request
from backend.ipfs2pid import IPFS2PID, PID2IPFS

def create_blueprint():
    bp = Blueprint('api', __name__)

# IPFS hash to Payment ID, json response
    @bp.route('ipfspid/<string:ipfs_hash>')
    def ipfspid(ipfs_hash):
        return jsonify({
            'pid': IPFS2PID(ipfs_hash)
            })

# Payment ID to IPFS hash, json response
    @bp.route('pidipfs/<string:payment_id>')
    def pidipfs(payment_id):
        return jsonify({
            'ipfs': PID2IPFS(payment_id)
            })

# Encrypted message to Payment ID, HTML response
    @bp.route('msgpid/')
    @bp.route('msgpid/<string:msg>')
    def msgpid(msg=None):
        msg = msg or request.args.get('msg')

        # Temporary fix to check if message is encrypted
        if 'BEGIN PGP' not in msg:
            return jsonify({'error': 'Message must be encrypted'})
        msg_data = msg + '\n' + strftime("%Y-%m-%d %H:%M:%S", gmtime())
        msg_hash = hashlib.md5('msg_data'.encode("utf-8")).hexdigest()
        filename = '%s.txt' % msg_hash
        ipfs_api = ipfsapi.connect(app.config['IPFS_ADDRESS'], app.config['IPFS_PORT'])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(msg_data)
        ipfs_response = ipfs_api.add(filename)
        os.remove(filename)
        payment_id = IPFS2PID(ipfs_response['Hash'])
        ipfs_hash = PID2IPFS(payment_id)

        return render_template('msgpid.html', ipfs_hash=ipfs_hash, payment_id=payment_id)

# Payment ID to Encrypted message, HTML response
    @bp.route('pid/')
    @bp.route('pid/<string:payment_id>')
    def pid(payment_id=None):
        payment_id = payment_id or request.args.get('payment_id')
        if len(payment_id) != 64:
            return jsonify({'error': 'Invalid Payment ID, please try again'})
        ipfs_hash = PID2IPFS(payment_id)
        ipfs_api = ipfsapi.connect(app.config['IPFS_ADDRESS'], app.config['IPFS_PORT'])
        
        def ipfs_cat(ipfs_hash, return_dict):
            return_dict['ipfs_response'] = ipfs_api.cat(ipfs_hash).decode("utf-8").rstrip('\r\n')
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        proc = multiprocessing.Process(target=ipfs_cat, args=(ipfs_hash, return_dict))
        proc.start()
        proc.join(app.config['IPFS_API_TIMEOUT'])
        if proc.is_alive() or 'ipfs_response' not in return_dict:
            proc.terminate()
            proc.join()
            return jsonify({'error': 'Invalid IPFS object'})
        else:
            msg = return_dict['ipfs_response']
            
        return render_template('ipfs.html', msg=msg)

    return bp

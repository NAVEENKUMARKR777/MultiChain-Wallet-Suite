// Utility Functions
function showLoading() {
    document.getElementById('loading-spinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading-spinner').style.display = 'none';
}

function showSuccess(message) {
    Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: message,
        confirmButtonColor: '#3182ce'
    });
}

function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Oops...',
        text: message,
        confirmButtonColor: '#3182ce'
    });
}

async function copyToClipboard(elementId) {
    const text = document.getElementById(elementId).textContent;
    try {
        await navigator.clipboard.writeText(text);
        const toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
        toast.fire({
            icon: 'success',
            title: 'Copied to clipboard!'
        });
    } catch (err) {
        showError('Failed to copy: ' + err);
    }
}

// Wallet Generation
document.getElementById('generate-wallet-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();

    const mnemonic = document.getElementById('mnemonic').value;
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mnemonic: mnemonic || undefined }),
        });

        if (!response.ok) throw new Error('Failed to generate wallet');
        const data = await response.json();

        // Display wallet info
        document.getElementById('wallet-info').style.display = 'block';
        document.getElementById('mnemonic-text').textContent = data.mnemonic;
        document.getElementById('eth-address').textContent = data.ethereum.address;
        document.getElementById('eth-private-key').textContent = data.ethereum.privateKey;
        document.getElementById('btc-address').textContent = data.bitcoin.address;
        document.getElementById('btc-private-key').textContent = data.bitcoin.privateKey;
        document.getElementById('trx-address').textContent = data.tron.address;
        document.getElementById('trx-private-key').textContent = data.tron.privateKey;

        showSuccess('Wallet generated successfully!');
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
});

// Send Transaction
document.getElementById('send-transaction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();

    const chain = document.getElementById('chain-select').value;
    const fromPrivateKey = document.getElementById('from-private-key').value;
    const toAddress = document.getElementById('to-address').value;
    const amount = document.getElementById('amount').value;

    try {
        const response = await fetch('/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chain,
                fromPrivateKey,
                toAddress,
                amount: parseFloat(amount)
            }),
        });

        if (!response.ok) throw new Error('Transaction failed');
        const data = await response.json();

        document.getElementById('transaction-result').style.display = 'block';
        document.getElementById('transaction-hash').textContent = data.transactionHash;
        showSuccess('Transaction sent successfully!');
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
});

// Check Balance
document.getElementById('check-balance-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();

    const chain = document.getElementById('balance-chain-select').value;
    const address = document.getElementById('balance-address').value;

    try {
        const response = await fetch('/balance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ chain, address }),
        });

        if (!response.ok) throw new Error('Failed to fetch balance');
        const data = await response.json();

        document.getElementById('balance-result').style.display = 'block';
        document.getElementById('balance-amount').textContent = `${data.balance} ${data.symbol}`;
        showSuccess('Balance fetched successfully!');
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
});

// Contract Management
async function loadContracts() {
    try {
        const response = await fetch('/contracts');
        if (!response.ok) throw new Error('Failed to load contracts');
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to load contracts');
        }
        
        const contractsList = document.getElementById('contracts-list');
        contractsList.innerHTML = '';
        
        // Handle the contracts object format
        Object.entries(data.contracts).forEach(([contractName, networks]) => {
            Object.entries(networks).forEach(([network, details]) => {
                const contractId = `contract-${network}-${details.address.substring(0, 8)}`;
                const contractCard = document.createElement('div');
                contractCard.className = 'card mb-3';
                contractCard.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">
                            ${contractName}
                            <span class="network-badge bg-info text-white">${network}</span>
                        </h5>
                        <p class="card-text">${details.description || 'No description available'}</p>
                        <p class="mb-2">
                            <strong>Address:</strong> 
                            <span id="${contractId}">${details.address}</span>
                            <i class="fas fa-copy copy-button ms-2" onclick="copyToClipboard('${contractId}')"></i>
                        </p>
                        <p class="text-muted small mb-3">Deployed: ${new Date(details.timestamp).toLocaleString()}</p>
                        ${contractName === 'MultiWithdraw' ? `
                            <button class="btn btn-primary" onclick="showMultiWithdrawForm('${details.address}')">
                                <i class="fas fa-paper-plane me-2"></i>
                                Use Contract
                            </button>
                        ` : ''}
                    </div>
                `;
                contractsList.appendChild(contractCard);
            });
        });
    } catch (error) {
        showError(error.message);
        console.error('Contract loading error:', error);
    }
}

// Update showMultiWithdrawForm to accept contract address
function showMultiWithdrawForm(contractAddress) {
    const form = document.getElementById('multiwithdraw-form');
    form.style.display = 'block';
    
    // Scroll to the form
    form.scrollIntoView({ behavior: 'smooth' });
    
    // Store contract address in a data attribute
    form.setAttribute('data-contract-address', contractAddress);
    
    // Add first recipient if none exist
    if (document.getElementsByClassName('recipient-group').length === 0) {
        addRecipient();
    }
}

// Update multi-withdraw form submission
document.getElementById('multi-withdraw-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading();

    const form = document.getElementById('multi-withdraw-form');
    const contractAddress = form.getAttribute('data-contract-address');
    const privateKey = document.getElementById('mw-private-key').value;
    const recipients = Array.from(document.getElementsByClassName('recipient-group')).map(group => ({
        address: group.querySelector('.recipient-address').value,
        amount: parseFloat(group.querySelector('.recipient-amount').value)
    }));

    try {
        const response = await fetch('/contract/multiwithdraw/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contractAddress,
                privateKey,
                recipients
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to send transaction');
        }

        const data = await response.json();
        showSuccess('Multi-withdraw transaction sent successfully!');
        
        // Show transaction details
        document.getElementById('transaction-result').style.display = 'block';
        document.getElementById('transaction-hash').textContent = data.transactionHash;
        
        // Clear form
        document.getElementById('mw-private-key').value = '';
        document.getElementById('recipients-container').innerHTML = '';
        addRecipient();
        
    } catch (error) {
        showError(error.message);
        console.error('Multi-withdraw error:', error);
    } finally {
        hideLoading();
    }
});

// Multi-withdraw functionality
function addRecipient() {
    const container = document.getElementById('recipients-container');
    const newGroup = document.createElement('div');
    newGroup.className = 'recipient-group';
    newGroup.innerHTML = `
        <i class="fas fa-times remove-recipient" onclick="this.parentElement.remove(); updateTotal();"></i>
        <div class="row">
            <div class="col-md-8 mb-3">
                <label class="form-label">Recipient Address</label>
                <input type="text" class="form-control recipient-address" required
                       placeholder="0x...">
            </div>
            <div class="col-md-4 mb-3">
                <label class="form-label">Amount (ETH)</label>
                <input type="number" step="0.000001" class="form-control recipient-amount" 
                       required onchange="updateTotal()">
            </div>
        </div>
    `;
    container.appendChild(newGroup);
    updateTotal();
}

function updateTotal() {
    const amounts = document.getElementsByClassName('recipient-amount');
    let total = 0;
    Array.from(amounts).forEach(input => {
        total += parseFloat(input.value || 0);
    });
    document.getElementById('total-eth').textContent = total.toFixed(6);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadContracts();
    // Add first recipient group
    addRecipient();
});

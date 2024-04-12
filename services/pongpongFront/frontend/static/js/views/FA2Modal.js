export default class FA2Modal {
    static attemptCount = 0; // 시도 횟수를 저장하는 정적 변수

    static async displayFA2Modal(userEmailAndCode, access_token) {
		const userEmail = userEmailAndCode.email;
        const code = userEmailAndCode.code;
		const backendURL = '/backend/send';

    
    

		const modalHTML = `
			<div id="fa2-modal" class="modal">
				<div class="modal-content">
					<h2>2FA Authentication</h2>
					<p><strong>${userEmail}</strong></p>
					<input id="user-input-code" type="text" placeholder="Enter your code here" />
					<button id="check-code-btn">Check Code</button>
					<p id="attempt-message"></p>
					<button id="close-modal-btn" disabled>Close</button>
				</div>
			</div>
			`;
		document.body.insertAdjacentHTML('beforeend', modalHTML);
		const modalElement = document.getElementById('fa2-modal');
		modalElement.style.display = 'block';
		
		document.getElementById('user-input-code').addEventListener('input', function() {
			this.value = this.value.replace(/[^0-9]/g, '');
		});

        document.getElementById('check-code-btn').addEventListener('click', async () => {
            const userInput = document.getElementById('user-input-code').value;
            FA2Modal.attemptCount++;
            if (userInput === code.toString()) {
				try {
                    const response = await fetch(backendURL, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${access_token}`
                        },
                        body: JSON.stringify({
                            userEmail: userEmail,
                            access_token: access_token
                        })
                    });

				

                    if (200 <= response.status && response.status < 300) {
                        document.getElementById('attempt-message').innerText = 'The code is right!';
                        localStorage.setItem('FA2_verified', true);
                        document.getElementById('close-modal-btn').disabled = false;
                    } else {
                        throw new Error('Server responded with an error.');
                    }
                } catch (error) {
                    document.getElementById('attempt-message').innerText = 'The code is right but your access token is invalid or a network error occurred!';
                    console.error('Error:', error);
                }
            } else {
                if (FA2Modal.attemptCount < 3) {
                    document.getElementById('attempt-message').innerText = `The code is invalid (${FA2Modal.attemptCount} / 3)`;
                } else {
                    localStorage.clear();
				
					window.location.href = '/';
                }
            }
        });

		document.getElementById('close-modal-btn').addEventListener('click', () => {
			modalElement.style.display = 'none';
			document.getElementById('go-to-game-select').disabled = false;
			document.dispatchEvent(new CustomEvent('fa2modalclosed'));
		});
		
    }
}

export default class LoginModal {
    static displayLoginModal() {
		const modal = `
			<div id="login-modal" class="modal">
				<div class="modal-content">
					<button id="loginBtn">LOG IN</button>
				</div>
			</div>
		`;
		document.body.innerHTML += modal;

		const modalElement = document.getElementById('login-modal');
		modalElement.style.display = 'block';

		document.getElementById('loginBtn').addEventListener('click', () => {
			this.redirectToLogin();
		});
    }

    static redirectToLogin() {
        const redirectUri = 'https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-38e1085a57405a04552b3a4b255d1b9a1708d9a23637ac72693e9469b06a779f&redirect_uri=https%3A%2F%2Fpongpongstest.duckdns.org%2Fget%2Fsecurity&response_type=code';
        window.location.href = redirectUri;
    }
}

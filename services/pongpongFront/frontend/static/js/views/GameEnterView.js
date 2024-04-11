import AbstractView from "./AbstractView.js";

export default class GameEnterView extends AbstractView {
    constructor(params) {
        super(params);
        this.setTitle('Game Enter');
		this.navigate = params.navigate;
    }

    async getHtml() {
        return `
            <h1>Game Enter page</h1>
            <button id="go-to-game-select" disabled>Go to Game Select</button>
			<h2>Wait if the button is disabled!</h2>
        `;
    }

	async addEventListeners() {
		if (localStorage.getItem('FA2_verified')) {
			document.getElementById('go-to-game-select').disabled = false;
		}
		document.getElementById('go-to-game-select').addEventListener('click', () => {
			this.navigate('/game/select');
		});
	}
}

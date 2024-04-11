import AbstractView from "./AbstractView.js";

export default class GameSelectView extends AbstractView {
    constructor(params) {
        super(params);
        this.setTitle('Game Select');
        this.navigate = params.navigate;
    }

    async getHtml() {
        return `
            <h1>Game Mode</h1>
            <div class="onoff-group" role="group" aria-label="OnOff button group">
                <input type="radio" class="btn-check" name="onlineOffline" id="offline-button" autocomplete="off">
                <label class="btn btn-outline-primary" for="offline-button">Offline</label>

                <input type="radio" class="btn-check" name="onlineOffline" id="online-button" autocomplete="off">
                <label class="btn btn-outline-primary" for="online-button">Online</label>
            </div>
            <div class="game-mode-group" role="group" aria-label="Players toggle button group"></div>
            <div id="nicknameInputs" style="display: none;"></div>
            <div class="form-group" id="roomNameGroup">
                <label for="roomName">Room Name</label>
                <input type="text" class="form-control" id="roomName" placeholder="Enter Room Name">
            </div>
            <button id="confirmButton" class="btn btn-primary" disabled>Confirm</button>
        `;
    }

    async addEventListeners() {
        const onlineOffline = document.getElementsByName('onlineOffline');
        const gameModeGroup = document.querySelector('.game-mode-group');
        const nicknameInputs = document.getElementById('nicknameInputs');
        const confirmButton = document.getElementById('confirmButton');
        const roomNameInput = document.getElementById('roomName');

        const bindGameModeChangeEventListener = () => {
            const gameModes = document.getElementsByName('gameMode');
            gameModes.forEach(mode => {
                mode.addEventListener('change', () => {
                    nicknameInputs.style.display = 'block';
                    updateInputs();
                });
            });
        };

        const updateGameModesAndInputs = () => {
            gameModeGroup.innerHTML = document.getElementById('offline-button').checked ? `
                <input type="radio" class="btn-check" name="gameMode" id="2p-button" autocomplete="off">
                <label class="btn btn-outline-primary" for="2p-button">1 vs 1</label>

                <input type="radio" class="btn-check" name="gameMode" id="Tour-button" autocomplete="off">
                <label class="btn btn-outline-primary" for="Tour-button">Tournament</label>
            ` : `
                <input type="radio" class="btn-check" name="gameMode" id="2p-button" autocomplete="off">
                <label class="btn btn-outline-primary" for="2p-button">1 vs 1</label>

                <input type="radio" class="btn-check" name="gameMode" id="4p-button" autocomplete="off">
                <label class="btn btn-outline-primary" for="4p-button">1 vs 1 vs 1 vs 1</label>
            `;
            bindGameModeChangeEventListener();
        };

        const updateInputs = () => {
            const gameModeSelected = document.querySelector('input[name="gameMode"]:checked')?.id;
            let inputHtml = '';

			if (document.getElementById('offline-button').checked) {
				if (gameModeSelected === '2p-button') {
					inputHtml = `<input type="text" class="form-control mb-2" placeholder="Nickname for Player 1">
								  <input type="text" class="form-control mb-2" placeholder="Nickname for Player 2">`;
				} else if (gameModeSelected === 'Tour-button') {
					inputHtml = `<input type="text" class="form-control mb-2" placeholder="Nickname for Player 1">
								  <input type="text" class="form-control mb-2" placeholder="Nickname for Player 2">
								  <input type="text" class="form-control mb-2" placeholder="Nickname for Player 3">
								  <input type="text" class="form-control mb-2" placeholder="Nickname for Player 4">`;
				}
			} else if (document.getElementById('online-button').checked) {
				inputHtml = `<input type="text" class="form-control mb-2" placeholder="Nickname for Player 1">`;
			}

            nicknameInputs.innerHTML = inputHtml;
			nicknameInputs.querySelectorAll('input').forEach(input => {
				input.addEventListener('input', () => {
					input.value = input.value.replace(/[^a-zA-Z0-9]/g, ''); // 영문자와 숫자만 유지
				});
			});
		
			// roomNameInput에 이벤트 리스너 추가
			roomNameInput.addEventListener('input', () => {
				roomNameInput.value = roomNameInput.value.replace(/[^a-zA-Z0-9]/g, ''); // 영문자와 숫자만 유지
			});
            checkInputs();
        };

		confirmButton.addEventListener('click', () => {
			const onlineOfflineValue = document.querySelector('input[name="onlineOffline"]:checked').id;
			const gameModeValue = document.querySelector('input[name="gameMode"]:checked').id;
            const roomNameValue = roomNameInput.value.trim();
	
			console.log(`Online/Offline: ${onlineOfflineValue}, Game Mode: ${gameModeValue}, Room Name: ${roomNameValue}`);
	
			// 경로 설정
			let path = "/";
			if (onlineOfflineValue === "offline-button") {
				if (gameModeValue === "2p-button") {
					path = "/game/off/2";
				} else if (gameModeValue === "Tour-button") {
					path = "/game/off/tour";
				}
			} else { // Online 모드
				if (gameModeValue === "2p-button") {
					path = "/game/on/2";
				} else if (gameModeValue === "4p-button") {
					path = "/game/on/4";
				}
			}
	
			// navigate 함수를 사용하여 지정된 경로로 이동
			this.navigate(path);
		});

        const checkInputs = () => {
			const onlineOfflineSelected = document.querySelector('input[name="onlineOffline"]:checked') !== null;
			const gameModeSelected = document.querySelector('input[name="gameMode"]:checked') !== null;
			const nicknameInputsFilled = Array.from(nicknameInputs.querySelectorAll('input')).every(input => input.value.trim() !== '');
			const roomNameFilled = document.getElementById('roomName').value.trim() !== '';
			const allFilled = onlineOfflineSelected && gameModeSelected && nicknameInputsFilled && roomNameFilled;

			confirmButton.disabled = !allFilled;

			if (allFilled) {
				const nicknames = Array.from(nicknameInputs.querySelectorAll('input')).map(input => input.value.trim());
				sessionStorage.removeItem('room_name');
				sessionStorage.removeItem('nicknames');
				sessionStorage.setItem('room_name', document.getElementById('roomName').value.trim());
				sessionStorage.setItem('nicknames', JSON.stringify(nicknames));
			}
        };

		onlineOffline.forEach(button => {
			button.addEventListener('change', updateGameModesAndInputs);
			button.addEventListener('change', updateInputs);
		});
        document.addEventListener('input', checkInputs);
    }
}

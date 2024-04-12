import AbstractView from "../AbstractView.js";
import * as THREE from 'three';
import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';

export default class OffTourView extends AbstractView {
	constructor(params) {
		super(params);
		this.setTitle('Offline Tournament');
		this.navigate = params.navigate;
		this._animate = this._animate.bind(this);
		this.barPositions = {
			bar1: {x: 0, y:0},
			bar2: {x: 0, y:0}
		};
		this.scoreBoard = {p1 : 0, p2: 0};
		this.ballPosition = {x:0, y:0};
		this.keyStates = {'a': false, 'd': false, 'j': false, 'l':false};
		this.gameSocket = null;
		this.playerIDs = {p1 : 1, p2 : 2};
	}

	async getHtml() {
		return `
		<div id="gameOverMessage">GAME OVER!!!</div>
		<div id="scoreBoard" style="text-align: center; margin-bottom: 20px;">
			<span id="player1Name">Loading...</span>: <span id="scorePlayer1">0</span> | 
			<span id="player2Name">Loading...</span>: <span id="scorePlayer2">0</span>
		</div>
		<div id="gameContainer" style="width: 800px; height: 600px; margin: auto;"></div>
	`;
	}

	async initialize() {
        
        
		this.roomName = sessionStorage.getItem("room_name");
		this.nicknames = JSON.parse(sessionStorage.getItem("nicknames"));
		if (!this.roomName || !this.nicknames) {
			this.navigate('/game/select');
			return;
		}
		sessionStorage.removeItem('room_name');
		sessionStorage.removeItem('nicknames');
		this.setupThreeJS();
        this.connectWebSocket(this.roomName);
    }

	setupThreeJS() {
		this._scene = new THREE.Scene();
		this._camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
		this._camera.position.set(0, 1, 20);

		this._renderer = new THREE.WebGLRenderer({ antialias: true });
		this._renderer.setSize(800,800);
		document.getElementById('gameContainer').appendChild(this._renderer.domElement); // 컨테이너에 렌더러 추가


		// document.body.appendChild(this._renderer.domElement);

		const controls = new OrbitControls(this._camera, this._renderer.domElement);
		controls.update();

		this._createBars();
		this._createBall(); // 공을 생성하는 메서드 호출
		this._createRectangle();

		this._animate();
	}

	_createBars() {
		// 바의 기하학적 모양과 재질을 정의합니다.
		const geometry = new THREE.BoxGeometry(2, 0.2, 0.2);
		const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
		this._bar1 = new THREE.Mesh(geometry, material);
		// 씬에 바를 추가합니다.
		this._scene.add(this._bar1);

		const geometry2 = new THREE.BoxGeometry(2, 0.2, 0.2);
		const material2 = new THREE.MeshBasicMaterial({ color: 0xff0000 });
		this._bar2 = new THREE.Mesh(geometry2, material2);
		this._scene.add(this._bar2);
	}

	_createBall() {
		// 공의 기하학적 모양과 재질을 정의합니다.
		const geometry = new THREE.SphereGeometry(0.2, 60, 6);
		const material = new THREE.MeshBasicMaterial({ color: 0xffff00 });
		this._ball = new THREE.Mesh(geometry, material);
		// 씬에 공을 추가합니다.
		this._scene.add(this._ball);
	}

	_createRectangle() {
		// 사각형의 테두리를 만들기 위한 PointsMaterial을 정의합니다.
		const material = new THREE.LineBasicMaterial({ color: 0xffffff });
	
		// 사각형의 테두리를 구성하는 점들을 정의합니다.
		const points = [];
		points.push(new THREE.Vector3(-11, 11, 0)); // 상단 왼쪽
		points.push(new THREE.Vector3(11, 11, 0));  // 상단 오른쪽
		points.push(new THREE.Vector3(11, -11, 0)); // 하단 오른쪽
		points.push(new THREE.Vector3(-11, -11, 0)); // 하단 왼쪽
		points.push(new THREE.Vector3(-11, 11, 0)); // 상단 왼쪽으로 돌아감 (사각형을 닫음)
	
		// 점들로부터 경로를 생성합니다.
		const geometry = new THREE.BufferGeometry().setFromPoints(points);
		// 경로와 재질로부터 사각형의 테두리를 만듭니다.
		const rectangle = new THREE.Line(geometry, material);
		// 씬에 사각형을 추가합니다.
		this._scene.add(rectangle);
	}

	_animate = () => {
		if (this.stopAnimation) return; // 플래그가 설정되어 있으면 루프 중지
	
		requestAnimationFrame(this._animate);
	
		if (this.playerIDs.p1 === 1) {
		  this._bar1.material.color.set(0x00FF00); // Player 1이면 초록색
		}
		if (this.playerIDs.p1 === 2) {
		  this._bar1.material.color.set(0xFF0000); // Player 2이면 빨간색
		} 
		if (this.playerIDs.p1 === 3) {
		  this._bar1.material.color.set(0x0000FF); // Player 3이면 파랑색
		}
		if (this.playerIDs.p1 === 4) {
		  this._bar1.material.color.set(0xFFFF00); // Player 3이면 파랑색
		}
	
		if (this.playerIDs.p2 === 1) {
		  this._bar2.material.color.set(0x00FF00); // Player 1이면 초록색
		}
		if (this.playerIDs.p2 === 2) {
		  this._bar2.material.color.set(0xFF0000); // Player 2이면 빨간색
		} 
		if (this.playerIDs.p2 === 3) {
		  this._bar2.material.color.set(0x0000FF); // Player 3이면 파랑색
		}
		if (this.playerIDs.p2 === 4) {
		  this._bar2.material.color.set(0xFFFF00); // Player 3이면 파랑색
		}
	  
		 
		// 바의 x 위치를 업데이트합니다. WebSocket을 통해 받은 barPosition.x 값을 사용합니다.
		this._bar1.position.set(this.barPositions.bar1.x, this.barPositions.bar1.y, 0);
		this._bar2.position.set(this.barPositions.bar2.x, this.barPositions.bar2.y, 0);
	
		this._ball.position.x = this.ballPosition.x * 1;
		this._ball.position.y = this.ballPosition.y * 1;
		// 렌더링
		this._renderer.render(this._scene, this._camera);
	  }
	
	  cleanup() {
		this.stopAnimation = true;

		// 웹소켓 연결이 있으면 종료한다.
		if (this.gameSocket) {
			this.gameSocket.close(); // 웹소켓 연결 종료
			this.gameSocket.onmessage = null; // 메시지 핸들러 제거
		}
	
		// sessionStorage에서 게임 관련 데이터 정리ß
		sessionStorage.removeItem('room_name');
		sessionStorage.removeItem('nicknames');
	}

	connectWebSocket(roomName) {
        const webSocketURL = `wss://pongpongstest.duckdns.org/b/ws/game/off/tour/${roomName}/`;

		
		this.gameSocket = new WebSocket(webSocketURL);

		
		
		document.addEventListener('keydown', (event) => {
			if (['a', 'd', 'j', 'l'].includes(event.key)) {
				this.keyStates[event.key] = true;
				sendKeyStates.call(this); // sendKeyStates를 호출할 때 this 바인딩
			}
		});
		
		document.addEventListener('keyup', (event) => {
			if (['a', 'd', 'j', 'l'].includes(event.key)) {
				this.keyStates[event.key] = false;
				sendKeyStates.call(this); // sendKeyStates를 호출할 때 this 바인딩
			}
		});

		// sendKeyStates가 클래스 메서드가 아닌 경우
		const sendKeyStates = function() {
			if (this.gameSocket.readyState === WebSocket.OPEN) {
				this.gameSocket.send(JSON.stringify(this.keyStates));
			}
		}.bind(this); // 이 부분은 connectWebSocket 메서드 안에서 this를 바인딩
	


		this.gameSocket.onclose = function(event) {
			if (event.code === 4001) {
				alert("This game is already full. Please join another game.");
				// 사용자가 확인을 누른 후 현재 페이지를 닫음
				this.navigate('/game/select');
			} else {
				console.error('WebSocket connection closed unexpectedly.');
			}
		};

		this.gameSocket.onmessage = (event)	=> {
			const data = JSON.parse(event.data);
		
			this.playerIDs.p1 = data.player1_id;
			this.playerIDs.p2 = data.player2_id;
			
			const player1NameElement = document.getElementById('player1Name');
			const player2NameElement = document.getElementById('player2Name');
			

			if (this.playerIDs.p1 == 1) player1NameElement.innerText = this.nicknames[0];
			if (this.playerIDs.p2 == 2) player2NameElement.innerText = this.nicknames[1];
			if (this.playerIDs.p1 == 3) player1NameElement.innerText = this.nicknames[2];
			if (this.playerIDs.p2 == 4) player2NameElement.innerText = this.nicknames[3];
			if (this.playerIDs.p1 == 2) player1NameElement.innerText = this.nicknames[1];
			if (this.playerIDs.p2 == 3) player2NameElement.innerText = this.nicknames[2];

			if (data.game_over_flag !== undefined) {
				if (data.game_over_flag == true) {
					var gameOverMessage = document.getElementById('gameOverMessage');
					gameOverMessage.style.display = 'block'; // 메시지 표시

					if (data.game_winner == 1) {
						if (data.player1_id == 1) {
							
							gameOverMessage.innerHTML = "Player " + this.nicknames[0] + " Wins!"; // Player 1 승리 메시지
							gameOverMessage.className = "winner1"; // 초록색 스타일 적용
						}
						if (data.player1_id == 3) {
							

							gameOverMessage.innerHTML = "Player " + this.nicknames[2] + " Wins!"; // Player 1 승리 메시지
							gameOverMessage.className = "winner3"; // 초록색 스타일 적용
						}
					} else if (data.game_winner == 2) {
						if (data.player2_id == 2) {
							

							gameOverMessage.innerHTML = "Player " + this.nicknames[1] + " Wins!"; // Player 2 승리 메시지
							gameOverMessage.className = "winner2"; // 빨간색 스타일 적용
						}
						if (data.player2_id == 4) {
							

							gameOverMessage.innerHTML = "Player " + this.nicknames[3] + " Wins!"; // Player 2 승리 메시지
							gameOverMessage.className = "winner4"; // 빨간색 스타일 적용
						} 
					} 
					setTimeout(function() {
						gameOverMessage.style.display = 'none';
					}, 3000);
				}
			}
			if (data.tournament_over_flag === true) {
				setTimeout(() => {
					this.navigate('/game/select'); // 3초 후 리다이렉션
				}, 3000);		
			}
		
			if (data.play_bar1_position !== undefined) {
				//
				this.barPositions.bar1.x = data.play_bar1_position.x;
				this.barPositions.bar1.y = data.play_bar1_position.y;
			}
			if (data.play_bar2_position !== undefined) {
				// 
				this.barPositions.bar2.x = data.play_bar2_position.x;
				this.barPositions.bar2.y = data.play_bar2_position.y;
			}
			if (data.ball_position !== undefined) {
				// 
				this.ballPosition.x = data.ball_position.x;
				this.ballPosition.y = data.ball_position.y;
			}
			if (data.score_player1 !== undefined && data.score_player2 !== undefined) {
				document.getElementById('scorePlayer1').innerText = data.score_player1;
				document.getElementById('scorePlayer2').innerText = data.score_player2;
			}
		};
		
		// 웹 소켓 강제 종료시 에러 처리 - 에러 로그 출력
		this.gameSocket.onclose = function(event) {
			console.error('chat socket closed unexpectedly');
		};
	}
}

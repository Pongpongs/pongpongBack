
import * as THREE from 'three';
import { OrbitControls } from 'https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js';

class App {
  
  constructor() {
    this._scene = new THREE.Scene();
    this._camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    this._camera.position.set(0, 1, 20);

    this._renderer = new THREE.WebGLRenderer({ antialias: true });
    this._renderer.setSize(800,800);
    document.getElementById('gameContainer').appendChild(this._renderer.domElement); // 컨테이너에 렌더러 추가


    document.body.appendChild(this._renderer.domElement);

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
    const material = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
    this._bar1 = new THREE.Mesh(geometry, material);
    // 씬에 바를 추가합니다.
    this._scene.add(this._bar1);

    const geometry2 = new THREE.BoxGeometry(2, 0.2, 0.2);
    const material2 = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
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
  

  _animate() {
    requestAnimationFrame(() => this._animate());
    // 바의 x 위치를 업데이트합니다. WebSocket을 통해 받은 barPosition.x 값을 사용합니다.
    this._bar1.position.set(barPositions.bar1.x, barPositions.bar1.y, 0);
    this._bar2.position.set(barPositions.bar2.x, barPositions.bar2.y, 0);

    this._ball.position.x = ballPosition.x * 1;
    this._ball.position.y = ballPosition.y * 1;
    // 렌더링
    this._renderer.render(this._scene, this._camera);
  }
}

// App 인스턴스 생성
window.onload = () => {
  const app = new App();
}
